"""Tests for Deepgram transcription service."""

from unittest.mock import MagicMock, patch

import pytest

import app.services.deepgram as deepgram_module
from app.services.deepgram import (
    DeepgramTranscriptionError,
    TranscriptionResult,
    transcribe_audio,
)


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset the singleton Deepgram client before each test."""
    deepgram_module._client = None
    yield
    deepgram_module._client = None


class TestDeepgramTranscriptionError:
    """Tests for DeepgramTranscriptionError exception."""

    def test_error_message(self) -> None:
        """Test exception message is stored correctly."""
        error = DeepgramTranscriptionError("Connection timeout")
        assert str(error) == "Connection timeout"

    def test_error_inheritance(self) -> None:
        """Test exception inherits from Exception."""
        error = DeepgramTranscriptionError("Test error")
        assert isinstance(error, Exception)


class TestTranscriptionResult:
    """Tests for TranscriptionResult named tuple."""

    def test_result_structure(self) -> None:
        """Test TranscriptionResult has correct fields."""
        result = TranscriptionResult(
            transcript="Test transcript",
            language_detected="fr",
            duration_seconds=30.5,
            latency_ms=1500.0,
        )
        assert result.transcript == "Test transcript"
        assert result.language_detected == "fr"
        assert result.duration_seconds == 30.5
        assert result.latency_ms == 1500.0

    def test_result_with_none_values(self) -> None:
        """Test TranscriptionResult with None values."""
        result = TranscriptionResult(
            transcript="",
            language_detected=None,
            duration_seconds=None,
            latency_ms=100.0,
        )
        assert result.transcript == ""
        assert result.language_detected is None
        assert result.duration_seconds is None


class TestTranscribeAudio:
    """Tests for transcribe_audio function."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create mock settings with API key."""
        settings = MagicMock()
        settings.deepgram_api_key = "test-api-key"
        settings.deepgram_model = "nova-3"
        return settings

    @pytest.fixture
    def mock_deepgram_response(self) -> MagicMock:
        """Create mock Deepgram API response object."""
        response = MagicMock()

        # Mock channel data
        alternative = MagicMock()
        alternative.transcript = "Le patient présente des douleurs lombaires."

        channel = MagicMock()
        channel.alternatives = [alternative]
        channel.detected_language = "fr"

        response.results.channels = [channel]
        response.metadata.duration = 30.5

        return response

    @pytest.mark.asyncio
    async def test_transcribe_success(
        self, mock_settings: MagicMock, mock_deepgram_response: MagicMock
    ) -> None:
        """Test successful transcription."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            # Setup mock
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.return_value = (
                mock_deepgram_response
            )

            # Test
            audio_data = b"fake audio data"
            result = await transcribe_audio(audio_data)

            # Verify
            assert result.transcript == "Le patient présente des douleurs lombaires."
            assert result.language_detected == "fr"
            assert result.duration_seconds == 30.5
            assert result.latency_ms > 0
            mock_client.listen.v1.media.transcribe_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcribe_with_language_parameter(
        self, mock_settings: MagicMock, mock_deepgram_response: MagicMock
    ) -> None:
        """Test transcription with specific language."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.return_value = (
                mock_deepgram_response
            )

            audio_data = b"fake audio data"
            result = await transcribe_audio(audio_data, language="de")

            assert result.transcript is not None
            # Verify language parameter was passed correctly
            call_kwargs = mock_client.listen.v1.media.transcribe_file.call_args[1]
            assert call_kwargs.get("language") == "de"
            assert call_kwargs.get("detect_language") is False

    @pytest.mark.asyncio
    async def test_transcribe_with_multi_language(
        self, mock_settings: MagicMock, mock_deepgram_response: MagicMock
    ) -> None:
        """Test transcription with multi-language detection."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.return_value = (
                mock_deepgram_response
            )

            audio_data = b"fake audio data"
            await transcribe_audio(audio_data, language="multi")

            # Verify multi detection settings
            call_kwargs = mock_client.listen.v1.media.transcribe_file.call_args[1]
            assert call_kwargs.get("language") is None
            assert call_kwargs.get("detect_language") is True

    @pytest.mark.asyncio
    async def test_transcribe_no_api_key(self) -> None:
        """Test error when API key is not configured."""
        mock_settings = MagicMock()
        mock_settings.deepgram_api_key = ""

        with patch("app.services.deepgram.get_settings", return_value=mock_settings):
            with pytest.raises(DeepgramTranscriptionError) as exc_info:
                await transcribe_audio(b"fake audio")

            assert "not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_whitespace_api_key(self) -> None:
        """Test error when API key is only whitespace."""
        mock_settings = MagicMock()
        mock_settings.deepgram_api_key = "   "

        with patch("app.services.deepgram.get_settings", return_value=mock_settings):
            with pytest.raises(DeepgramTranscriptionError) as exc_info:
                await transcribe_audio(b"fake audio")

            assert "not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_empty_channels(self, mock_settings: MagicMock) -> None:
        """Test error when Deepgram returns empty channels."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.results.channels = []
            mock_client.listen.v1.media.transcribe_file.return_value = mock_response

            with pytest.raises(DeepgramTranscriptionError) as exc_info:
                await transcribe_audio(b"fake audio")

            assert "No channels" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_no_alternatives(self, mock_settings: MagicMock) -> None:
        """Test error when Deepgram returns no alternatives."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_channel = MagicMock()
            mock_channel.alternatives = []
            mock_response.results.channels = [mock_channel]
            mock_client.listen.v1.media.transcribe_file.return_value = mock_response

            with pytest.raises(DeepgramTranscriptionError) as exc_info:
                await transcribe_audio(b"fake audio")

            assert "No alternatives" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_api_error(self, mock_settings: MagicMock) -> None:
        """Test error handling for API failures."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
            patch("app.services.deepgram.sentry_sdk") as mock_sentry,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.side_effect = Exception(
                "API timeout"
            )

            with pytest.raises(DeepgramTranscriptionError) as exc_info:
                await transcribe_audio(b"fake audio")

            assert "Transcription failed" in str(exc_info.value)
            mock_sentry.capture_exception.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcribe_retry_on_connection_error(
        self, mock_settings: MagicMock, mock_deepgram_response: MagicMock
    ) -> None:
        """Test retry logic on transient ConnectionError."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
            patch("app.services.deepgram.sentry_sdk"),
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # First call fails with ConnectionError (retryable), second succeeds
            mock_client.listen.v1.media.transcribe_file.side_effect = [
                ConnectionError("Transient error"),
                mock_deepgram_response,
            ]

            result = await transcribe_audio(b"fake audio")
            assert result.transcript == "Le patient présente des douleurs lombaires."
            assert mock_client.listen.v1.media.transcribe_file.call_count == 2

    @pytest.mark.asyncio
    async def test_transcribe_no_retry_on_generic_exception(
        self, mock_settings: MagicMock
    ) -> None:
        """Test that generic exceptions are NOT retried (only ApiError, ConnectionError, TimeoutError)."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
            patch("app.services.deepgram.sentry_sdk"),
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Generic ValueError should NOT be retried
            mock_client.listen.v1.media.transcribe_file.side_effect = ValueError(
                "Unexpected error"
            )

            with pytest.raises(DeepgramTranscriptionError):
                await transcribe_audio(b"fake audio")

            # Should only be called once (no retry for ValueError)
            assert mock_client.listen.v1.media.transcribe_file.call_count == 1

    @pytest.mark.asyncio
    async def test_transcribe_empty_transcript(
        self, mock_settings: MagicMock
    ) -> None:
        """Test handling of empty transcript (silence)."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_alternative = MagicMock()
            mock_alternative.transcript = ""  # Empty transcript
            mock_channel = MagicMock()
            mock_channel.alternatives = [mock_alternative]
            mock_channel.detected_language = "fr"
            mock_response.results.channels = [mock_channel]
            mock_response.metadata.duration = 5.0
            mock_client.listen.v1.media.transcribe_file.return_value = mock_response

            result = await transcribe_audio(b"fake audio")
            assert result.transcript == ""
            assert result.language_detected == "fr"

    @pytest.mark.asyncio
    async def test_singleton_client_reused(
        self, mock_settings: MagicMock, mock_deepgram_response: MagicMock
    ) -> None:
        """Test that the singleton client is reused across calls."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.return_value = (
                mock_deepgram_response
            )

            # Call twice
            await transcribe_audio(b"fake audio 1")
            await transcribe_audio(b"fake audio 2")

            # DeepgramClient constructor should only be called once (singleton)
            assert mock_client_class.call_count == 1
            # But transcribe_file should be called twice
            assert mock_client.listen.v1.media.transcribe_file.call_count == 2


class TestTranscriptionLanguages:
    """Tests for language detection and configuration."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create mock settings with API key."""
        settings = MagicMock()
        settings.deepgram_api_key = "test-api-key"
        settings.deepgram_model = "nova-3"
        return settings

    def _create_mock_response(self, transcript: str, language: str) -> MagicMock:
        """Create a mock Deepgram response."""
        response = MagicMock()
        alternative = MagicMock()
        alternative.transcript = transcript
        channel = MagicMock()
        channel.alternatives = [alternative]
        channel.detected_language = language
        response.results.channels = [channel]
        response.metadata.duration = 30.0
        return response

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "language,expected",
        [
            ("fr", "fr"),
            ("de", "de"),
            ("en", "en"),
        ],
    )
    async def test_supported_languages(
        self, mock_settings: MagicMock, language: str, expected: str
    ) -> None:
        """Test transcription with different language settings."""
        with (
            patch("app.services.deepgram.get_settings", return_value=mock_settings),
            patch("app.services.deepgram.DeepgramClient") as mock_client_class,
        ):
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.listen.v1.media.transcribe_file.return_value = (
                self._create_mock_response("Test transcript", expected)
            )

            result = await transcribe_audio(b"fake audio", language=language)
            assert result.language_detected == expected
