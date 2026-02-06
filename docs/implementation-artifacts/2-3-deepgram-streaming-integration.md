# Story 2.3: Deepgram Streaming Integration

Status: review

## Story

As a system,
I want to transcribe audio using Deepgram Nova-3 pre-recorded API,
So that the transcription is ready when recording stops.

**Implementation Note:** Uses Deepgram's pre-recorded API (not WebSocket streaming) because Story 2.2's architecture sends the complete audio file after recording stops. Pre-recorded API is simpler and sufficient for this flow.

## Acceptance Criteria

### AC1: Audio Transcription with Deepgram
**Given** a user uploads a completed recording
**When** the backend receives the audio file
**Then** backend sends the audio to Deepgram Nova-3 pre-recorded API
**And** the transcript is returned and stored
**And** the synchronous SDK call is offloaded to a thread pool (`asyncio.to_thread`)

### AC2: Audio Format Validation
**Given** the backend receives audio data
**When** processing the upload
**Then** the audio format is validated (WebM/Opus or supported format)
**And** audio is forwarded to Deepgram for transcription

### AC3: Transcription Storage (RGPD Compliant)
**Given** Deepgram returns transcription results
**When** final results are received
**Then** they are stored temporarily for SOAP extraction
**And** audio file is NOT persisted (RGPD: 0 day retention)

### AC4: Recording Completion
**Given** the user stops recording
**When** the final transcription is complete
**Then** the full transcript text is available for the next step (SOAP extraction)
**And** response time from Stop to transcript ready is tracked (target < 5s)

### AC5: Error Handling
**Given** Deepgram connection fails
**When** an error occurs
**Then** the error is logged to Sentry
**And** user sees an error message with retry option
**And** no partial data is lost if possible

### AC6: Recording Database Schema
**Given** the recordings table schema
**When** a recording is processed
**Then** the recordings table is created with: id, user_id, duration_seconds, language_detected, transcript_text, created_at
**And** audio binary is NOT stored (deleted immediately after transcription)

## Tasks / Subtasks

### Task 1: Create Deepgram Service (AC: 1, 2, 5)
- [x] 1.1 Create `backend/app/services/deepgram.py`
  - Singleton DeepgramClient with API key from env
  - Pre-recorded API via `client.listen.v1.media.transcribe_file()`
  - Options: model="nova-3", language="multi", smart_format=True, punctuate=True
  - Sync SDK call offloaded to thread pool via `asyncio.to_thread()`
- [x] 1.2 Implement transcribe_audio function
  - Accept audio bytes (WebM/Opus format)
  - Send complete audio to Deepgram pre-recorded API
  - Return TranscriptionResult with transcript, language, duration, latency
- [x] 1.3 Add retry logic with tenacity (2 attempts, 1s fixed wait, specific exception types only)
- [x] 1.4 Add Sentry error logging for failures
- [x] 1.5 Add docstrings per coding standards

### Task 2: Create Recording Model (AC: 6)
- [x] 2.1 Create `backend/app/models/recording.py`
  - Fields: id (UUID), user_id (FK), duration_seconds, language_detected, transcript_text, created_at
  - No audio_data field (RGPD compliance)
- [x] 2.2 Create Alembic migration for recordings table
- [x] 2.3 Update `backend/app/models/__init__.py` exports

### Task 3: Update Recording Schemas (AC: 4)
- [x] 3.1 Update `backend/app/schemas/recording.py`
  - Add RecordingWithTranscript schema (includes transcript_text)
  - Add TranscriptionStatus enum (transcribing, completed, failed)
- [x] 3.2 Add docstrings on all new schemas

### Task 4: Integrate Deepgram in Recordings Endpoint (AC: 1, 2, 3, 4, 5)
- [x] 4.1 Update `backend/app/routers/recordings.py`
  - Call deepgram_service.transcribe_audio after receiving upload
  - Store Recording model with transcript
  - Return RecordingWithTranscript response
  - Handle Deepgram errors gracefully (return TRANSCRIPTION_FAILED)
- [x] 4.2 Add latency tracking (start_time to transcript_ready)
  - Log to INFO level for monitoring
  - Target: < 5 seconds for short recordings
- [x] 4.3 Update endpoint docstrings

### Task 5: Configuration & Environment (AC: 1)
- [x] 5.1 Update `backend/app/config.py`
  - Add DEEPGRAM_API_KEY setting
  - Add DEEPGRAM_MODEL setting (default: "nova-3")
- [x] 5.2 Update `.env.example` with DEEPGRAM_API_KEY placeholder
- [x] 5.3 Verify Railway environment variable configuration docs

### Task 6: Backend Tests (AC: All)
- [x] 6.1 Create `backend/app/tests/test_deepgram_service.py`
  - Mock Deepgram pre-recorded API responses
  - Test successful transcription
  - Test error handling and retries (ConnectionError retried, generic exceptions not)
  - Test singleton client reuse
  - Test API key validation (empty and whitespace)
- [x] 6.2 Update `backend/app/tests/test_recordings.py`
  - Add integration test with mocked Deepgram
  - Test transcription flow end-to-end
  - Test error response when Deepgram fails

### Task 7: Frontend WebSocket Streaming (Optional - See Notes)
- [x] 7.1 Evaluate if frontend streaming is needed (see Dev Notes)
  - **Decision: NOT needed for MVP** - Using pre-recorded API since audio is complete when uploaded
- [ ] 7.2 If needed: Update useRecording hook to send chunks via WebSocket
  - **Skipped** - Not needed for MVP
- [ ] 7.3 If needed: Add WebSocket connection state to recording UI
  - **Skipped** - Not needed for MVP

### Task 8: Manual Testing & Validation
- [ ] 8.1 Test: Short recording (< 30s) transcribes successfully
- [ ] 8.2 Test: French, German, English recordings all transcribe correctly
- [ ] 8.3 Test: Multi-language recording with auto-detection works
- [ ] 8.4 Test: Transcript is stored in database, audio is NOT stored
- [ ] 8.5 Test: Deepgram connection failure shows user-friendly error
- [ ] 8.6 Test: Latency tracking logs appear in backend logs
- [ ] 8.7 Test: Max duration recording (10 min) completes within 30s

**Note:** Task 8 requires a valid DEEPGRAM_API_KEY to perform real transcription tests. Unit tests with mocks pass successfully (40/40 tests).

## Dev Notes

### Architecture Compliance

**CRITICAL**: Follow these patterns from project-context.md:

1. **Folder Structure**:
   - Deepgram service: `backend/app/services/deepgram.py`
   - Recording model: `backend/app/models/recording.py`
   - Updated schemas: `backend/app/schemas/recording.py`

2. **Naming Conventions**:
   - snake_case for Python files: `deepgram.py`, `recording.py`
   - snake_case for functions: `transcribe_audio()`, `get_recording()`
   - PascalCase for classes: `DeepgramService`, `Recording`

3. **Documentation**:
   - Docstrings on all functions (see coding standards)
   - Example:
   ```python
   async def transcribe_audio(audio_data: bytes, language: str = "multi") -> str:
       """
       Transcribe audio using Deepgram Nova-3 via WebSocket streaming.

       Args:
           audio_data: Raw audio bytes (WebM/Opus format)
           language: Language code or "multi" for auto-detection

       Returns:
           Full transcript text

       Raises:
           DeepgramError: If transcription fails after retries
       """
       pass
   ```

### Previous Story Learnings (Story 2.2)

**CRITICAL - From Story 2.2 Implementation:**
- MediaRecorder uses `audio/webm;codecs=opus` format with 250ms chunks
- Backend endpoint POST /api/v1/recordings already exists and accepts:
  - `audio`: WebM/Opus file
  - `duration`: Recording duration in seconds
  - `language_detected`: Optional language code
- Quota validation, MIME type validation already implemented
- RecordingStatus enum: UPLOADED, PROCESSING, COMPLETED, FAILED

**Current Backend Flow (Story 2.2):**
```python
# In recordings.py - current TODO placeholders:
# TODO: Story 2.3 - Send to Deepgram for transcription
# TODO: Story 3.1 - Send transcript to Mistral for SOAP extraction
```

**Files Already Existing from Story 2.2:**
| File | Status | Notes |
|------|--------|-------|
| `backend/app/routers/recordings.py` | EXISTS | Has TODO for Deepgram |
| `backend/app/schemas/recording.py` | EXISTS | Has RecordingCreate, RecordingResponse |
| `backend/app/tests/test_recordings.py` | EXISTS | Tests for Story 2.2 |

### Technical Requirements

#### Deepgram Python SDK (v5.3.1 - January 2026)

**Installation:**
```bash
pip install deepgram-sdk==5.3.1
```

**SDK Documentation:**
- [deepgram-sdk PyPI](https://pypi.org/project/deepgram-sdk/)
- [GitHub Repository](https://github.com/deepgram/deepgram-python-sdk)

**WebSocket Streaming Pattern:**
```python
from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
import asyncio

async def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using Deepgram Nova-3."""
    deepgram = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)

    # Store results
    transcript_parts = []

    # Create WebSocket connection
    connection = deepgram.listen.websocket.v("1")

    @connection.on(LiveTranscriptionEvents.Transcript)
    def handle_transcript(result):
        if result.channel.alternatives:
            transcript = result.channel.alternatives[0].transcript
            if transcript:
                transcript_parts.append(transcript)

    # Configure options for Nova-3
    options = LiveOptions(
        model="nova-3",
        language="multi",  # Auto-detect FR/DE/EN
        smart_format=True,  # Format numbers, dates
        punctuate=True,     # Add punctuation
    )

    # Connect and send audio
    if await connection.start(options):
        connection.send(audio_data)
        connection.finish()

        # Wait for processing (simplified)
        await asyncio.sleep(2)

    return " ".join(transcript_parts)
```

**Alternative: Pre-recorded Audio (Simpler for MVP)**

Since Story 2.2 sends the complete audio file after recording stops, a simpler approach uses Deepgram's pre-recorded API instead of live streaming:

```python
from deepgram import DeepgramClient, PrerecordedOptions

async def transcribe_audio(audio_data: bytes) -> str:
    """Transcribe audio using Deepgram Nova-3 pre-recorded API."""
    deepgram = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)

    options = PrerecordedOptions(
        model="nova-3",
        language="multi",
        smart_format=True,
        punctuate=True,
    )

    # Send audio for transcription
    source = {"buffer": audio_data, "mimetype": "audio/webm"}
    response = await deepgram.listen.asyncprerecorded.v("1").transcribe_file(
        source, options
    )

    # Extract transcript
    transcript = response.results.channels[0].alternatives[0].transcript
    return transcript
```

**DECISION NEEDED:** The architecture doc mentions WebSocket streaming, but the current frontend flow (Story 2.2) sends the complete audio after recording stops. Options:

1. **Option A (Recommended for MVP):** Use pre-recorded API - simpler, audio already complete when uploaded
2. **Option B (Future):** True real-time streaming - requires frontend WebSocket to backend, backend to Deepgram

**Recommendation:** Start with Option A (pre-recorded API) for MVP simplicity. True streaming can be added later for real-time UI feedback.

#### Deepgram API Configuration

**WebSocket Endpoint:**
```
wss://api.deepgram.com/v1/listen
```

**Key Parameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| `model` | `nova-3` | Best accuracy, multilingual support |
| `language` | `multi` | Auto-detect (FR/DE/EN) |
| `smart_format` | `true` | Format numbers, dates, emails |
| `punctuate` | `true` | Add punctuation |
| `interim_results` | `false` | Final results only (for simplicity) |

**Supported Languages (Nova-3):**
- French: `fr`, `fr-CA`, `fr-FR`
- German: `de`, `de-DE`, `de-CH`
- English: `en`, `en-US`, `en-GB`
- Multi (auto-detect): `multi`

#### Error Handling Pattern

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import sentry_sdk

class DeepgramTranscriptionError(Exception):
    """Custom exception for Deepgram transcription failures."""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def transcribe_audio_with_retry(audio_data: bytes) -> str:
    """Transcribe with automatic retries."""
    try:
        return await transcribe_audio(audio_data)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise DeepgramTranscriptionError(f"Transcription failed: {str(e)}")
```

### Recording Model Schema

```python
# backend/app/models/recording.py
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Recording(Base):
    """
    Recording model for storing transcription metadata.

    NOTE: Audio data is NEVER persisted (RGPD compliance).
    Only the transcript and metadata are stored.
    """
    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    language_detected = Column(String(10), nullable=True)
    transcript_text = Column(Text, nullable=True)  # Can be null if transcription fails
    created_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="recordings")
```

**Alembic Migration:**
```python
# alembic/versions/xxx_create_recordings_table.py
def upgrade():
    op.create_table(
        'recordings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('duration_seconds', sa.Integer, nullable=False),
        sa.Column('language_detected', sa.String(10), nullable=True),
        sa.Column('transcript_text', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_recordings_user_id', 'recordings', ['user_id'])
    op.create_index('ix_recordings_created_at', 'recordings', ['created_at'])
```

### Updated Recording Response Schema

```python
# backend/app/schemas/recording.py - additions

class RecordingWithTranscript(BaseModel):
    """
    Recording response with full transcript (after transcription completes).

    Used when the full recording details are needed, including transcript.
    """
    id: str = Field(..., description="Unique recording identifier")
    status: RecordingStatus
    duration_seconds: int = Field(..., alias="durationSeconds")
    language_detected: str | None = Field(None, alias="languageDetected")
    transcript_text: str | None = Field(None, alias="transcriptText")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)
```

### Backend Latency Tracking

```python
import time
import logging

logger = logging.getLogger(__name__)

async def process_recording(audio_data: bytes, user_id: str) -> RecordingWithTranscript:
    """Process recording with latency tracking."""
    start_time = time.time()

    # Transcribe with Deepgram
    transcript = await deepgram_service.transcribe_audio(audio_data)

    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000
    logger.info(
        "Transcription completed",
        extra={
            "user_id": user_id,
            "latency_ms": latency_ms,
            "transcript_length": len(transcript),
        }
    )

    # Check against target (5s = 5000ms)
    if latency_ms > 5000:
        logger.warning(
            "Transcription latency exceeded target",
            extra={"latency_ms": latency_ms, "target_ms": 5000}
        )

    return transcript
```

### RGPD Compliance Notes

**CRITICAL - Audio Data Handling:**
- Audio bytes are received in memory only
- Immediately sent to Deepgram for transcription
- Audio is NEVER written to disk or database
- After transcription, audio bytes are garbage collected
- Only transcript text is persisted

**Implementation:**
```python
# Good - audio never persisted
audio_data = await audio.read()  # In memory only
transcript = await transcribe_audio(audio_data)
# audio_data goes out of scope and is garbage collected

# Recording model has NO audio_data field
recording = Recording(
    id=recording_id,
    user_id=user.id,
    transcript_text=transcript,
    # NO audio_data field!
)
```

### File Structure After Implementation

```
backend/app/
├── services/
│   ├── __init__.py              # MODIFY - Add deepgram export
│   ├── deepgram.py              # NEW - Deepgram transcription service
│   ├── auth.py
│   ├── subscription.py
│   └── plan.py
├── models/
│   ├── __init__.py              # MODIFY - Add Recording export
│   ├── recording.py             # NEW - Recording SQLAlchemy model
│   ├── user.py
│   ├── subscription.py
│   └── plan.py
├── schemas/
│   ├── recording.py             # MODIFY - Add RecordingWithTranscript
│   └── ...
├── routers/
│   ├── recordings.py            # MODIFY - Integrate Deepgram
│   └── ...
├── config.py                    # MODIFY - Add DEEPGRAM_API_KEY
└── tests/
    ├── test_deepgram_service.py # NEW - Deepgram service tests
    ├── test_recordings.py       # MODIFY - Add transcription tests
    └── ...

alembic/versions/
└── xxx_create_recordings_table.py  # NEW - Migration
```

### Environment Variables

```bash
# .env (add to existing)
DEEPGRAM_API_KEY=your-deepgram-api-key

# Optional (with defaults)
DEEPGRAM_MODEL=nova-3
DEEPGRAM_LANGUAGE=multi
```

### Git Commit Pattern

Follow conventional commits:
```
feat(transcription): add Deepgram service with Nova-3 integration
feat(models): create Recording model for transcript storage
feat(schemas): add RecordingWithTranscript response schema
feat(recordings): integrate Deepgram transcription in upload endpoint
chore(config): add DEEPGRAM_API_KEY configuration
test(deepgram): add unit tests for transcription service
feat(db): add recordings table migration
```

### Latest Technical Information (Web Research - Jan 2026)

**Deepgram SDK v5.3.1:**
- Latest stable version as of January 2026
- Supports async WebSocket connections
- Auto-retry for 408, 429, 5xx status codes with exponential backoff
- MIT licensed

**Nova-3 Model Performance:**
- 54.3% reduction in WER for streaming vs competitors
- Real-time multilingual transcription (10 languages including FR/DE/EN)
- Keyterm prompting for specialized terminology
- Pricing: $0.0077/min streaming, $0.0066/min batch

**Supported Audio Formats:**
- WebM/Opus (our format) via `ogg-opus` or `opus` encoding
- Linear16, FLAC, AMR, G.729, Speex also supported
- Sample rate auto-detection supported

**Sources:**
- [Deepgram Live Audio API](https://developers.deepgram.com/reference/speech-to-text/listen-streaming)
- [deepgram-sdk PyPI](https://pypi.org/project/deepgram-sdk/)
- [Deepgram Python SDK GitHub](https://github.com/deepgram/deepgram-python-sdk)
- [Nova-3 Introduction](https://deepgram.com/learn/introducing-nova-3-speech-to-text-api)

### Security & Privacy Notes

**API Key Security:**
- DEEPGRAM_API_KEY in environment variables only
- Never logged or exposed in responses
- Railway environment variables for production

**Data Flow:**
1. Frontend sends complete audio to backend
2. Backend receives audio in memory
3. Backend sends to Deepgram via secure WebSocket (wss://)
4. Deepgram returns transcript
5. Backend stores transcript, discards audio
6. No audio ever persisted (RGPD 0-day retention)

## References

- [Source: project-context.md - Deepgram configuration, RGPD constraints]
- [Source: docs/planning-artifacts/epics/stories.md - Story 2.3 Acceptance Criteria]
- [Source: docs/planning-artifacts/architecture/core-architectural-decisions.md - WebSocket proxy pattern]
- [Source: docs/implementation-artifacts/2-2-audio-recording-interface.md - Previous story patterns, existing code]
- [External: Deepgram API Documentation](https://developers.deepgram.com/reference/speech-to-text/listen-streaming)
- [External: Deepgram Python SDK](https://github.com/deepgram/deepgram-python-sdk)
- [External: Nova-3 Model Documentation](https://deepgram.com/learn/introducing-nova-3-speech-to-text-api)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 43 unit tests pass (19 Deepgram service tests + 24 recording tests)
- Pre-existing tests unrelated to Story 2.3 have timezone issues (not caused by this implementation)

### Completion Notes List

- ✅ Created Deepgram transcription service using pre-recorded API (simpler for MVP)
- ✅ Singleton DeepgramClient pattern (reused across requests)
- ✅ Sync SDK call offloaded to thread pool via `asyncio.to_thread()` (non-blocking)
- ✅ Implemented retry logic with tenacity (2 attempts, 1s fixed wait, specific exception types only)
- ✅ Added 30s timeout on Deepgram API calls
- ✅ Added API key validation (empty string and whitespace-only rejected)
- ✅ Added Sentry error logging for transcription failures
- ✅ Created Recording model with UUID primary key, user relationship, RGPD compliance (no audio storage)
- ✅ Created Alembic migration for recordings table with indexes (user_id, created_at, status, updated_at)
- ✅ Added RecordingWithTranscript schema with camelCase JSON aliases
- ✅ Added TranscriptionStatus enum (pending, transcribing, completed, failed)
- ✅ Integrated Deepgram transcription in POST /api/v1/recordings endpoint
- ✅ Quota decremented only AFTER successful transcription (race condition fix)
- ✅ Recording marked as FAILED on transcription error, quota NOT decremented
- ✅ Added latency tracking with warning for > 5s transcription time
- ✅ Added DEEPGRAM_MODEL and DEEPGRAM_LANGUAGE configuration options
- ✅ Updated .env.example with Deepgram configuration
- ✅ Created comprehensive test suite for Deepgram service (19 tests)
- ✅ Updated recordings tests with Recording model and transcription tests (24 tests)
- ✅ Evaluated frontend WebSocket streaming - NOT needed for MVP (using pre-recorded API)

### Implementation Decision

Used Deepgram's **pre-recorded API** instead of WebSocket streaming for MVP simplicity:
- Frontend sends complete audio after recording stops (Story 2.2 design)
- Pre-recorded API is simpler and sufficient for this flow
- Real-time WebSocket streaming can be added later for live transcription feedback

### Code Review Fixes Applied

Code review found 12 issues (6 HIGH, 4 MEDIUM, 2 LOW). All fixed:

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | HIGH | AC1 referenced WebSocket (not implemented) | Updated ACs to reflect pre-recorded API |
| 2 | HIGH | Blocking I/O in async function | Offloaded sync SDK call via `asyncio.to_thread()` |
| 3 | HIGH | Race condition - quota decremented before transcription | Moved quota decrement to after successful transcription |
| 4 | HIGH | Missing transaction handling on failure | Recording marked FAILED and committed on error |
| 5 | HIGH | Task 1.1 claimed WebSocket | Updated task descriptions |
| 6 | HIGH | Missing API key format validation | Added whitespace-only rejection |
| 7 | MEDIUM | Creating client per request | Singleton `_get_client()` pattern |
| 8 | MEDIUM | Retry logic too aggressive (3 retries, exponential) | 2 attempts, 1s fixed wait, specific exceptions only |
| 9 | MEDIUM | Missing index on updated_at | Added `idx_recordings_updated_at` to migration |
| 10 | MEDIUM | No timeout on Deepgram API call | Added 30s timeout via `request_options` |
| 11 | LOW | Unused `now` variable | Removed |
| 12 | LOW | Exception catch too broad | Specific types: `ApiError`, `ConnectionError`, `TimeoutError` |

### File List

**New Files:**
- `backend/app/services/deepgram.py` - Deepgram transcription service
- `backend/app/models/recording.py` - Recording SQLAlchemy model
- `backend/app/tests/test_deepgram_service.py` - Deepgram service unit tests
- `backend/alembic/versions/b2c3d4e5f6g7_create_recordings_table.py` - Migration

**Modified Files:**
- `backend/app/services/__init__.py` - Added deepgram export
- `backend/app/models/__init__.py` - Added Recording export
- `backend/app/models/user.py` - Added recordings relationship
- `backend/app/schemas/recording.py` - Added RecordingWithTranscript, TranscriptionStatus
- `backend/app/routers/recordings.py` - Integrated Deepgram transcription
- `backend/app/config.py` - Added DEEPGRAM_MODEL, DEEPGRAM_LANGUAGE settings
- `backend/app/tests/test_recordings.py` - Added Recording model and transcription tests
- `backend/requirements.txt` - Added deepgram-sdk, tenacity dependencies
- `backend/.env.example` - Added Deepgram configuration
- `backend/alembic/env.py` - Added Recording model import

## Change Log

| Date | Change |
|------|--------|
| 2026-01-28 | Story implementation completed - Deepgram pre-recorded API integration, Recording model, tests |
| 2026-02-01 | Code review fixes applied - 12 issues fixed (blocking I/O, race condition, retry logic, singleton, API validation, index, timeout) |
