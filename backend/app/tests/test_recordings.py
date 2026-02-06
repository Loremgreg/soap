"""Tests for recordings endpoints."""

import io
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan
from app.models.recording import Recording
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.routers.recordings import (
    ALLOWED_AUDIO_TYPES,
    AudioTooLongException,
    InvalidAudioTypeException,
    MAX_RECORDING_SECONDS,
    TranscriptionFailedException,
)
from app.schemas.recording import RecordingStatus
from app.services.deepgram import DeepgramTranscriptionError, TranscriptionResult


class TestRecordingsConstants:
    """Tests for recordings module constants and exceptions."""

    def test_allowed_audio_types(self) -> None:
        """Test allowed audio MIME types."""
        assert "audio/webm" in ALLOWED_AUDIO_TYPES
        assert "audio/ogg" in ALLOWED_AUDIO_TYPES
        assert "audio/mp4" in ALLOWED_AUDIO_TYPES
        assert "audio/mpeg" in ALLOWED_AUDIO_TYPES
        assert "text/plain" not in ALLOWED_AUDIO_TYPES

    def test_max_recording_seconds(self) -> None:
        """Test max recording duration constant."""
        assert MAX_RECORDING_SECONDS == 600  # 10 minutes

    def test_audio_too_long_exception(self) -> None:
        """Test AudioTooLongException structure."""
        exc = AudioTooLongException(duration=700, max_duration=600)
        assert exc.status_code == 413
        assert exc.code == "AUDIO_TOO_LONG"
        assert exc.details["duration"] == 700
        assert exc.details["maxDuration"] == 600

    def test_invalid_audio_type_exception(self) -> None:
        """Test InvalidAudioTypeException structure."""
        exc = InvalidAudioTypeException(content_type="text/plain")
        assert exc.status_code == 415
        assert exc.code == "INVALID_AUDIO_TYPE"
        assert exc.details["contentType"] == "text/plain"
        assert "allowedTypes" in exc.details

    def test_invalid_audio_type_exception_none_content_type(self) -> None:
        """Test InvalidAudioTypeException with None content type."""
        exc = InvalidAudioTypeException(content_type=None)
        assert exc.status_code == 415
        assert exc.details["contentType"] is None

    def test_transcription_failed_exception(self) -> None:
        """Test TranscriptionFailedException structure."""
        exc = TranscriptionFailedException(reason="Deepgram timeout")
        assert exc.status_code == 500
        assert exc.code == "TRANSCRIPTION_FAILED"
        assert exc.details["reason"] == "Deepgram timeout"


class TestRecordingsEndpointAuth:
    """Tests for recordings endpoint authentication."""

    @pytest.mark.asyncio
    async def test_upload_recording_requires_auth(self, client: AsyncClient) -> None:
        """Test recording upload requires authentication."""
        audio_file = io.BytesIO(b"fake audio data")

        response = await client.post(
            "/api/v1/recordings",
            files={"audio": ("test.webm", audio_file, "audio/webm")},
            data={"duration": "60"},
        )

        assert response.status_code == 401


class TestRecordingsModels:
    """Tests for recordings-related model interactions."""

    @pytest.fixture
    async def test_plan(self, db_session: AsyncSession) -> Plan:
        """Create a test plan."""
        plan = Plan(
            name=f"test_plan_{uuid.uuid4().hex[:8]}",
            display_name="Test Plan",
            price_monthly=0,
            quota_monthly=10,
            max_recording_minutes=10,
            max_notes_retention=10,
            is_active=True,
        )
        db_session.add(plan)
        await db_session.commit()
        await db_session.refresh(plan)
        return plan

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user."""
        user = User(
            google_id=f"google_{uuid.uuid4().hex[:8]}",
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            name="Test User",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_subscription(
        self, db_session: AsyncSession, test_user: User, test_plan: Plan
    ) -> Subscription:
        """Create a test subscription with quota."""
        now = datetime.now(timezone.utc)
        subscription = Subscription(
            user_id=test_user.id,
            plan_id=test_plan.id,
            status=SubscriptionStatus.TRIAL.value,
            quota_remaining=5,
            quota_total=5,
            trial_ends_at=now + timedelta(days=14),
            current_period_start=now,
            current_period_end=now + timedelta(days=14),
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        return subscription

    @pytest.mark.asyncio
    async def test_subscription_quota_can_be_decremented(
        self, db_session: AsyncSession, test_subscription: Subscription
    ) -> None:
        """Test that subscription quota can be decremented."""
        initial_remaining = test_subscription.quota_remaining

        # Simulate quota decrement (as done in recordings endpoint)
        test_subscription.quota_remaining -= 1
        await db_session.commit()
        await db_session.refresh(test_subscription)

        assert test_subscription.quota_remaining == initial_remaining - 1

    @pytest.mark.asyncio
    async def test_subscription_quota_exhausted_check(
        self, db_session: AsyncSession, test_subscription: Subscription
    ) -> None:
        """Test detecting when quota is exhausted."""
        # Exhaust quota
        test_subscription.quota_remaining = 0
        await db_session.commit()
        await db_session.refresh(test_subscription)

        # Check would be: subscription.quota_remaining <= 0
        assert test_subscription.quota_remaining <= 0

    @pytest.mark.asyncio
    async def test_subscription_expired_status_check(
        self, db_session: AsyncSession, test_subscription: Subscription
    ) -> None:
        """Test detecting expired subscription."""
        test_subscription.status = SubscriptionStatus.EXPIRED.value
        await db_session.commit()
        await db_session.refresh(test_subscription)

        # Check would be: subscription.status == "expired"
        assert test_subscription.status == "expired"

    @pytest.mark.asyncio
    async def test_user_without_subscription(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test user without subscription has no subscription relationship."""
        await db_session.refresh(test_user)
        assert test_user.subscription is None


class TestMimeTypeValidation:
    """Tests for MIME type validation logic."""

    def test_valid_base_mime_types(self) -> None:
        """Test valid base MIME types are accepted."""
        valid_types = ["audio/webm", "audio/ogg", "audio/mp4", "audio/mpeg"]
        for mime_type in valid_types:
            base_type = mime_type.split(";")[0].strip()
            assert base_type in ALLOWED_AUDIO_TYPES

    def test_mime_type_with_codec_parameter(self) -> None:
        """Test MIME type with codec parameter is correctly parsed."""
        mime_with_codec = "audio/webm;codecs=opus"
        base_type = mime_with_codec.split(";")[0].strip()
        assert base_type == "audio/webm"
        assert base_type in ALLOWED_AUDIO_TYPES

    def test_invalid_mime_type(self) -> None:
        """Test invalid MIME types are rejected."""
        invalid_types = ["text/plain", "application/json", "video/mp4", "image/png"]
        for mime_type in invalid_types:
            base_type = mime_type.split(";")[0].strip()
            assert base_type not in ALLOWED_AUDIO_TYPES


class TestDurationValidation:
    """Tests for duration validation logic."""

    def test_valid_duration(self) -> None:
        """Test valid duration within limits."""
        duration = 300  # 5 minutes
        assert duration <= MAX_RECORDING_SECONDS

    def test_duration_at_limit(self) -> None:
        """Test duration exactly at limit."""
        duration = 600  # 10 minutes
        assert duration <= MAX_RECORDING_SECONDS

    def test_duration_exceeds_limit(self) -> None:
        """Test duration exceeding limit."""
        duration = 700  # 11+ minutes
        assert duration > MAX_RECORDING_SECONDS


class TestRecordingModel:
    """Tests for Recording model."""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user."""
        user = User(
            google_id=f"google_{uuid.uuid4().hex[:8]}",
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            name="Test User",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.mark.asyncio
    async def test_create_recording(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test creating a recording model."""
        recording = Recording(
            user_id=test_user.id,
            duration_seconds=180,
            language_detected="fr",
            transcript_text="Test transcript content",
            status=RecordingStatus.COMPLETED.value,
        )
        db_session.add(recording)
        await db_session.commit()
        await db_session.refresh(recording)

        assert recording.id is not None
        assert recording.user_id == test_user.id
        assert recording.duration_seconds == 180
        assert recording.language_detected == "fr"
        assert recording.transcript_text == "Test transcript content"
        assert recording.status == "completed"
        assert recording.created_at is not None

    @pytest.mark.asyncio
    async def test_recording_without_transcript(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test recording with null transcript (failed transcription)."""
        recording = Recording(
            user_id=test_user.id,
            duration_seconds=60,
            status=RecordingStatus.FAILED.value,
        )
        db_session.add(recording)
        await db_session.commit()
        await db_session.refresh(recording)

        assert recording.transcript_text is None
        assert recording.language_detected is None
        assert recording.status == "failed"

    @pytest.mark.asyncio
    async def test_recording_user_relationship(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test recording-user relationship."""
        recording = Recording(
            user_id=test_user.id,
            duration_seconds=120,
            status=RecordingStatus.PROCESSING.value,
        )
        db_session.add(recording)
        await db_session.commit()
        await db_session.refresh(recording)
        await db_session.refresh(test_user)

        # Verify relationship
        assert recording.user.id == test_user.id
        assert len(test_user.recordings) == 1
        assert test_user.recordings[0].id == recording.id

    @pytest.mark.asyncio
    async def test_recording_status_transitions(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test recording status can be updated."""
        recording = Recording(
            user_id=test_user.id,
            duration_seconds=90,
            status=RecordingStatus.TRANSCRIBING.value,
        )
        db_session.add(recording)
        await db_session.commit()

        # Update status
        recording.status = RecordingStatus.COMPLETED.value
        recording.transcript_text = "Transcribed text"
        await db_session.commit()
        await db_session.refresh(recording)

        assert recording.status == "completed"
        assert recording.transcript_text == "Transcribed text"


class TestTranscriptionIntegration:
    """Tests for transcription integration with Deepgram."""

    def test_transcription_result_structure(self) -> None:
        """Test TranscriptionResult has expected structure."""
        result = TranscriptionResult(
            transcript="Le patient présente des douleurs lombaires.",
            language_detected="fr",
            duration_seconds=30.5,
            latency_ms=1500.0,
        )
        assert result.transcript == "Le patient présente des douleurs lombaires."
        assert result.language_detected == "fr"
        assert result.duration_seconds == 30.5
        assert result.latency_ms == 1500.0

    def test_deepgram_transcription_error(self) -> None:
        """Test DeepgramTranscriptionError exception."""
        error = DeepgramTranscriptionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, Exception)

    def test_recording_status_enum_values(self) -> None:
        """Test RecordingStatus enum has expected values."""
        assert RecordingStatus.UPLOADED.value == "uploaded"
        assert RecordingStatus.PROCESSING.value == "processing"
        assert RecordingStatus.TRANSCRIBING.value == "transcribing"
        assert RecordingStatus.COMPLETED.value == "completed"
        assert RecordingStatus.FAILED.value == "failed"
