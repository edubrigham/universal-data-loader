# Azure Speech-to-Text Integration - Specification

## 1. Overview

This feature integrates Azure Speech-to-Text capabilities into the application, allowing users to transcribe audio files. It will primarily leverage the Azure Speech SDK for robust interaction with the service, including support for custom speech models.

## 2. Functional Scope

*   **Authentication:** Securely connect to Azure Speech services using API key and region.
*   **Custom Model Support:** Utilize a specific custom speech model endpoint ID if provided.
*   **Audio Input:** Accept a path to a local audio file (initially WAV format) or a path to a directory containing audio files. If a directory is provided, all supported audio files within that directory (non-recursively by default, potentially recursive as an option) should be processed.
*   **Transcription:** Submit the audio to Azure and retrieve the transcribed text. For directory input, this implies batch or sequential processing of multiple files.
*   **Result Handling:**
    *   Provide the full recognized text.
    *   Indicate success, no match (silence), or cancellation.
    *   If canceled, provide details about the cancellation reason and error.
*   **Configuration:** Load credentials (`SPEECH_KEY`, `SPEECH_REGION`, `SPEECH_ENDPOINT_ID`) from environment variables (e.g., via a `.env` file).
*   **Error Reporting:** Clearly report issues such as authentication failures, file access problems, or service errors. For directory input, errors should be reported per-file, allowing successful transcriptions to proceed.

## 3. Technical Scope

*   **Primary Method:** Python Azure Speech SDK (`azure-cognitiveservices-speech`).
*   **Core SDK Components:**
    *   `speechsdk.SpeechConfig`: For service configuration (key, region, custom model endpoint).
    *   `speechsdk.audio.AudioConfig`: To specify the audio input source (file-based).
    *   `speechsdk.SpeechRecognizer`: To perform the recognition task.
    *   `recognize_once_async().get()`: For single-shot recognition from a file.
    *   `SpeechRecognitionResult`: To process and interpret the outcome.
*   **Alternative (Fallback/Reference):** REST API calls (POST to `https://<REGION>.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1`) can be considered for specific scenarios if the SDK presents limitations, but the SDK is the preferred method.
*   **Output:** The primary output will be the transcribed text string. For single file input, a single result. For directory input, a collection of results (e.g., a list of result objects, or a dictionary mapping filenames to results). Additional metadata (reason for result, duration, offset, cancellation details) will be available from the SDK's result object and should be accessible if needed by the calling code.

## 4. UI Treatments / Layout Options

Since this feature is primarily a backend/SDK integration, the "UI" refers to how a developer might interact with it via an API or how a simple CLI tool might expose it.

**Option 1: Simple CLI Tool Interface**

*   **Interaction:** Command-line arguments to specify input file or directory, and optionally the output file/directory or display to console.
    ```bash
    # Single file
    python transcribe_cli.py --input_path "path/to/audio.wav" 
    # Output: displays transcription to console

    python transcribe_cli.py --input_path "path/to/audio.wav" --output_path "path/to/transcription.txt"
    # Output: saves transcription to file

    # Directory
    python transcribe_cli.py --input_path "path/to/audio_directory/" --output_path "path/to/transcriptions_directory/"
    # Output: saves transcriptions to files in the output directory, matching input filenames
    ```
*   **Pros:** Easy to use for quick tests, good for scripting, supports batch processing.
*   **Cons:** Limited interactivity, not suitable for web applications directly.
*   **Visual (Console Output for Directory):**
    ```
    Starting transcription for directory: path/to/audio_directory/
    Processing file1.wav... SUCCESS. Transcription saved to path/to/transcriptions_directory/file1.txt
    Processing file2.wav... FAILED (AuthenticationFailure). See logs for details.
    Processing file3.wav... SUCCESS. Transcription saved to path/to/transcriptions_directory/file3.txt
    ...
    Batch Succeeded: 2, Failed: 1
    ```
    Or for an error:
    ```
    Starting transcription for: path/to/audio.wav
    Status: CANCELED
    Reason: AuthenticationFailure
    Error Details: WebSocket upgrade failed with an authentication error (401). Please check your subscription key and region.
    ```

**Option 2: API Endpoint (e.g., FastAPI)**

*   **Interaction:** A POST request to an API endpoint (e.g., `/transcribe` for single file, `/transcribe_batch` for directory) or a single endpoint that intelligently handles file/directory paths.
    ```json
    // Request (single file by path)
    POST /api/v1/transcribe
    {
      "audio_file_path": "/shared_volume/audio.wav"
    }

    // Request (directory by path)
    POST /api/v1/transcribe_batch 
    {
      "audio_directory_path": "/shared_volume/audio_files/"
    }

    // Response (Success - Batch)
    HTTP 200 OK
    {
      "batch_summary": {
        "total_files": 5,
        "successful": 4,
        "failed": 1
      },
      "results": [
        {"original_file": "file1.wav", "status": "RecognizedSpeech", "transcription": "..."},
        {"original_file": "file2.wav", "status": "Canceled", "error_details": "..."},
        // ... more results
      ]
    }
    ```
*   **Pros:** Integrates well with web applications, allows for more complex input/output handling.
*   **Cons:** Requires setting up an API service. Batch processing status reporting needs careful design.
*   **Trade-offs:** For batch, the API could return immediately and provide a job ID for status polling, or stream results, or wait for completion (suitable for smaller batches).

**Option 3: Python Function/Class Interface (for SDK users)**

*   **Interaction:** Python functions or class methods that developers can call. Could have separate methods for single file and directory, or one method that handles both.
    ```python
    from azure_transcriber import AzureTranscriber, TranscriptionResult, BatchTranscriptionResult

    # Assuming transcriber is initialized with config (key, region, endpoint_id)
    transcriber = AzureTranscriber()

    # Single file
    result_single: TranscriptionResult = transcriber.transcribe_file("path/to/audio.wav")
    if result_single.success:
        print(f"Transcription (single): {result_single.text}")
    else:
        print(f"Error (single): {result_single.error_details}")

    # Directory
    batch_result: BatchTranscriptionResult = transcriber.transcribe_directory("path/to/audio_folder/")
    print(f"Batch Summary: Processed {batch_result.total_files}, Succeeded: {len(batch_result.successful_transcriptions)}, Failed: {len(batch_result.failed_transcriptions)}")
    for success_result in batch_result.successful_transcriptions:
        print(f"  Success ({success_result.original_file}): {success_result.transcription.text}")
    for failed_result in batch_result.failed_transcriptions:
        print(f"  Failed ({failed_result.original_file}): {failed_result.transcription.error_details}")

    ```
*   **Pros:** Most direct integration for Python developers, maximum flexibility for both single and batch.
*   **Cons:** Requires developers to handle the surrounding application logic and result aggregation for batches.
*   **Trade-offs:** One smart `transcribe(path)` method vs. `transcribe_file(path)` and `transcribe_directory(path)`. Explicit methods are often clearer. Returning a dedicated batch result object is more structured.

**Recommendation:**

For a backend library, **Option 3 (Python Function/Class Interface)** is the primary deliverable as it provides the core logic. 
**Option 1 (CLI Tool)** can be a useful supplementary utility for testing and simple use cases.
**Option 2 (API Endpoint)** would be a separate feature built on top of the core library if a web service is required.

## 5. Output Format Considerations

*   **SDK `SpeechRecognitionResult`:** This object is rich and contains:
    *   `result.text`: The recognized speech.
    *   `result.reason`: Enum (`RecognizedSpeech`, `NoMatch`, `Canceled`).
    *   `result.offset`: Offset in ticks (100 nanoseconds).
    *   `result.duration`: Duration in ticks.
    *   `result.properties`: Additional properties.
    *   `result.cancellation_details`: If `reason` is `Canceled`, this object (`CancellationDetails`) contains `reason` (enum like `Error`, `EndOfStream`) and `error_details` (string).
*   **REST API (detailed format):** JSON response includes `RecognitionStatus`, `DisplayText`, `Offset`, `Duration`. `NBest` can also be requested.

For the core Python function (Option 3), returning a custom Pydantic model encapsulating these key details would be beneficial for consumers of the library, providing a clear and typed interface to the transcription outcome. 