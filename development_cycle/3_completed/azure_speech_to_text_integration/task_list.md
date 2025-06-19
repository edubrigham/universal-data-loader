# Task List: Azure Speech-to-Text Integration

## I. Core Configuration & Dependencies
- [x] **Task 1: Update Project Dependencies:**
    - [x] Add `azure-cognitiveservices-speech` to `pyproject.toml` (or `requirements.txt`).
    - [x] Ensure `pydantic` and `pydantic-settings` (for `BaseSettings`) are present.
- [x] **Task 2: Enhance Application Configuration (`src/core/config.py`):**
    - [x] Update/Create `AppSettings` (Pydantic `BaseSettings`) to include:
        - `SPEECH_KEY: Optional[str]`
        - `SPEECH_REGION: Optional[str]`
        - `SPEECH_ENDPOINT_ID: Optional[str]`
    - [x] Ensure these settings are loaded from `.env`.

## II. Transcription Module Data Models (`src/transcription/models.py`)
- [x] **Task 3: Define Pydantic Model for Single Transcription Result:**
    - [x] Create `AzureTranscriptionResult(BaseModel)` with fields:
        - `success: bool`
        - `text: Optional[str]`
        - `status_reason: str`
        - `error_details: Optional[str]`
        - `raw_result_reason: Optional[str]`
        - `raw_cancellation_reason: Optional[str]`
        - `duration_ms: Optional[float]`
        - `offset_ms: Optional[float]`
        - `original_file_path: Optional[FilePath]`
- [x] **Task 4: Define Pydantic Models for Batch Transcription Results:**
    - [x] Create `BatchTranscriptionReportItem(BaseModel)` with fields:
        - `original_file: FilePath`
        - `transcription_result: AzureTranscriptionResult`
    - [x] Create `AzureBatchTranscriptionResult(BaseModel)` with fields:
        - `total_files_processed: int`
        - `successful_transcriptions: int`
        - `failed_transcriptions: int`
        - `results: List[BatchTranscriptionReportItem]`

## III. Azure Speech Service Implementation (`src/transcription/azure_speech_service.py`)
- [x] **Task 5: Create `AzureSpeechService` Class:**
    - [x] Implement `__init__(self, speech_key: str, speech_region: str, speech_endpoint_id: Optional[str] = None)`:
        - Store credentials.
        - Raise `ValueError` if key or region is missing.
        - Initialize `speechsdk.SpeechConfig`.
        - Set `endpoint_id` on `speech_config` if provided.
- [x] **Task 6: Implement `_transcribe_single_file(self, audio_file_path: Path) -> AzureTranscriptionResult` Method:**
    - [x] Create `speechsdk.audio.AudioConfig(filename=str(audio_file_path))`.
    - [x] Create `speechsdk.SpeechRecognizer`.
    - [x] Call `recognize_once_async().get()` for transcription.
    - [x] Convert result (duration, offset) from ticks to milliseconds.
    - [x] Map `result.reason` (RecognizedSpeech, NoMatch, Canceled) to `AzureTranscriptionResult` fields.
        - For `NoMatch`, populate `error_details` from `result.no_match_details`.
        - For `Canceled`, populate `error_details` and `raw_cancellation_reason` from `result.cancellation_details`.
    - [x] Include `original_file_path` in the returned `AzureTranscriptionResult`.
    - [x] Implement try-except block for SDK exceptions, mapping them to an `AzureTranscriptionResult` with `success=False`.
- [x] **Task 7: Implement `transcribe_path(self, input_path: str, recursive: bool = False, audio_extensions: List[str] = None) -> Union[AzureTranscriptionResult, AzureBatchTranscriptionResult]` Method:**
    - [x] Handle `input_path` being a file:
        - Check if file extension is in `audio_extensions` (default `['.wav']`).
        - If supported, call `_transcribe_single_file`.
        - If not supported, return an `AzureTranscriptionResult` indicating the error.
    - [x] Handle `input_path` being a directory:
        - Use `pathlib.Path.glob()` to find audio files based on `audio_extensions` and `recursive` flag.
        - Initialize `successful_count`, `failed_count`, and `batch_results_list`.
        - For each found audio file:
            - Call `_transcribe_single_file`.
            - Append a `BatchTranscriptionReportItem` to `batch_results_list`.
            - Increment `successful_count` or `failed_count`.
        - Return `AzureBatchTranscriptionResult` populated with summary and `batch_results_list`.
    - [x] Handle `input_path` not being a valid file or directory:
        - Return an `AzureTranscriptionResult` indicating an invalid path error.
    - [x] Ensure necessary imports: `os`, `glob`, `Path`, `List`, `Union`.

## IV. Command-Line Interface (CLI) - Optional but Recommended for Testing (`scripts/transcribe_azure_cli.py`)
- [x] **Task 8: Develop CLI Script:**
    - [x] Use `argparse` to define command-line arguments:
        - `--input_path` (required)
        - `--output_path` (optional, for saving results)
        - `--recursive` (optional flag for directory processing)
        - `--speech_key` (optional, can also rely on env)
        - `--speech_region` (optional, can also rely on env)
        - `--speech_endpoint_id` (optional, can also rely on env)
    - [x] Load configuration (prioritize CLI args, then environment variables via `AppSettings`).
    - [x] Instantiate `AzureSpeechService`.
    - [x] Call `transcribe_path`.
    - [x] Handle single `AzureTranscriptionResult`:
        - Print transcription or error to console.
        - If `output_path` is a file, save text or error.
    - [x] Handle `AzureBatchTranscriptionResult`:
        - Print summary (total, success, fail) to console.
        - If `output_path` is a directory, save each successful transcription to a `.txt` file named after the original audio file, and log errors for failed files (e.g., in a central log file or individual error files).

## V. Unit Testing (`tests/`)
- [x] **Task 9: Test Configuration Loading (`tests/core/test_config.py`):**
    - [x] Test that `SPEECH_KEY`, `SPEECH_REGION`, `SPEECH_ENDPOINT_ID` are correctly loaded by `AppSettings`.
- [x] **Task 10: Test Transcription Data Models (`tests/transcription/test_models.py`):**
    - [x] Test instantiation and serialization of `AzureTranscriptionResult`.
    - [x] Test instantiation and serialization of `BatchTranscriptionReportItem`.
    - [x] Test instantiation and serialization of `AzureBatchTranscriptionResult`.
- [x] **Task 11: Test `AzureSpeechService` (`tests/transcription/test_azure_speech_service.py`):**
    - [x] Test `AzureSpeechService.__init__`:
        - Successful initialization with and without `speech_endpoint_id`.
        - `ValueError` if `speech_key` or `speech_region` is missing.
    - [ ] **(Skipped)** Mock `azure.cognitiveservices.speech` SDK components for `_transcribe_single_file` tests:
        - Test successful recognition: `result.reason == RecognizedSpeech`.
        - Test no speech match: `result.reason == NoMatch`.
        - Test cancellation: `result.reason == Canceled` (simulate different `CancellationReason` and `error_details`).
        - Test SDK raising an exception during `recognize_once_async().get()`.
    - [ ] Test `transcribe_path` logic:
        - Input is a valid single audio file (mock `_transcribe_single_file` - *this part will now focus on `transcribe_path`'s handling rather than deep `_transcribe_single_file` mocking*).
        - Input is a single file with an unsupported extension.

## VI. Documentation & Finalization
- [x] **Task 12: Write Docstrings:**
    - [x] Add comprehensive Google-style docstrings to all new classes, methods, and modules (`config.py`, `models.py`, `azure_speech_service.py`, `transcribe_azure_cli.py`).
- [x] **Task 13: Update Project README (Optional):**
    - [x] If a CLI tool is created, add a section to the main `README.md` on how to use it for Azure transcription.
- [x] **Task 14: Code Review & Refinement:**
    - [x] Review code for clarity, efficiency, and adherence to project standards.
    - [x] Refactor as needed.

This list provides a structured approach to implementing the Azure Speech-to-Text integration. 