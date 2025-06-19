# Feature Specification: Main Orchestration Pipeline

**Status:** Planning
**Feature ID:** FEAT-MAIN-ORCHESTRATOR
**Version:** 1.0
**Last Updated:** 2024-08-01
**Authors:** AI Assistant, User

## 1. Introduction & Goals

The project currently relies on separate scripts for transcribing audio (`scripts/transcribe_azure_cli.py`) and evaluating transcriptions (`scripts/evaluate_transcriptions.py`). This requires users to manually execute multiple commands and manage intermediate files, which can be inefficient, especially for iterative testing and larger datasets.

**Goal:** To establish `main.py` (at the project root) as the central orchestrator for the entire transcription and evaluation workflow. This script will provide a unified command-line interface to process either a single audio file or a directory of audio files, handling the necessary steps from transcription to evaluation.

**Benefits:**
*   **Unified Entry Point:** Simplifies the user experience by providing a single command to run various pipeline configurations.
*   **Improved Efficiency:** Automates the multi-step process, reducing manual effort and potential for errors.
*   **Streamlined Workflow:** Facilitates easier management of inputs, outputs, and configurations for both single-file and batch operations.
*   **Enhanced Testability:** Allows for quicker cycles of transcription and evaluation.

## 2. User Stories

*   **As a developer, I want to** use `python main.py` with specific arguments to transcribe a single audio file and immediately get its evaluation report, **so that I can** quickly test changes or specific audio samples.
*   **As a data processor, I want to** use `python main.py` to process an entire directory of audio files, generating transcriptions and a consolidated evaluation report, **so that I can** efficiently process datasets and assess overall transcription quality.
*   **As a project manager, I want** a clear and simple way for the team to run the core transcription and evaluation tasks, **so that I can** ensure consistency and reduce onboarding time for new team members.

## 3. Requirements

### Functional Requirements

*   **R1: Central Orchestrator (`main.py`)**
    *   **R1.1:** `main.py` at the project root shall be the primary entry point for initiating transcription and/or evaluation workflows.
*   **R2: Command-Line Interface (CLI) for `main.py`**
    *   **R2.1: Mode of Operation:** `main.py` must support two primary modes based on input arguments:
        *   **Single File Mode:** Process a single audio file.
        *   **Batch Mode:** Process all recognized audio files within a specified directory.
    *   **R2.2: Core Arguments:**
        *   `--input_path PATH`: (Required) Path to either a single audio file or a directory containing audio files.
        *   `--output_dir DIRECTORY_PATH`: (Required) Path to a directory where all outputs (transcriptions, reports) will be saved. The orchestrator should create subdirectories within this `output_dir` for clarity (e.g., `transcriptions/`, `evaluations/`).
        *   `--config_file PATH`: (Optional) Path to a YAML or JSON configuration file. This file can provide default values for other arguments and settings (e.g., Azure credentials, evaluation parameters). CLI arguments should override config file settings.
    *   **R2.3: Transcription Control Arguments (passed to transcription module):**
        *   `--recursive`: (Batch Mode) If `input_path` is a directory, scan recursively. (Defaults to False)
        *   `--audio_extensions EXT1 EXT2 ...`: List of audio file extensions to process. (Defaults to `.wav`)
        *   (Azure credentials like `speech_key`, `speech_region`, `speech_endpoint_id` should primarily be managed via `.env` and `src.core.config` or the optional `--config_file`. Direct CLI pass-through to `main.py` for these could be considered but might clutter the interface.)
    *   **R2.4: Evaluation Control Arguments:**
        *   `--run_evaluation`: (Flag) If set, perform evaluation after transcription. (Defaults to False, or could be True if a ground truth path is provided).
        *   `--ground_truth_file PATH`: Path to the ground truth JSON file. Required if `--run_evaluation` is set (or if evaluation is implicitly enabled).
        *   `--evaluation_normalization_mode MODE`: (Optional) Specify normalization mode for evaluation (e.g., 'default', 'enhanced').
*   **R3: Workflow Logic**
    *   **R3.1: Single File Mode (`--input_path` is a file):**
        1.  Perform transcription of the single audio file using the adapted `AzureSpeechService` or by calling a refactored `scripts/transcribe_azure_cli.py` function.
        2.  Save the transcription to `[output_dir]/transcriptions/[original_filename].txt`.
        3.  If `--run_evaluation` is enabled and `--ground_truth_file` is provided:
            a.  Prepare a temporary single-entry hypothesis JSON (as defined in previous feature FEAT-INTEGRATED-EVAL).
            b.  Call the evaluation logic from `scripts/evaluate_transcriptions.py`.
            c.  Save the evaluation report to `[output_dir]/evaluations/[original_filename]_eval_report.json`.
    *   **R3.2: Batch Mode (`--input_path` is a directory):**
        1.  Identify all target audio files in `input_path` (respecting `--recursive` and `--audio_extensions`).
        2.  For each audio file:
            a.  Perform transcription.
            b.  Save transcription to `[output_dir]/transcriptions/[original_filename].txt`.
        3.  After all transcriptions are complete, create a consolidated hypothesis JSON file at `[output_dir]/evaluations/hypotheses_batch.json` from all generated transcription text files.
        4.  If `--run_evaluation` is enabled and `--ground_truth_file` is provided:
            a.  Call the evaluation logic from `scripts/evaluate_transcriptions.py` using the `hypotheses_batch.json` and the provided ground truth file.
            b.  Save the comprehensive evaluation report to `[output_dir]/evaluations/batch_eval_report.json`.
*   **R4: Module Interaction:**
    *   **R4.1:** `main.py` will import and use functionality from `src.transcription.azure_speech_service` (or a refactored version of `scripts/transcribe_azure_cli.py`) for transcription tasks.
    *   **R4.2:** `main.py` will import and use functions from `scripts.evaluate_transcriptions` for evaluation tasks.
    *   **R4.3:** Existing scripts (`transcribe_azure_cli.py`, `evaluate_transcriptions.py`) might need refactoring to expose their core logic as callable functions/classes if they are currently too CLI-centric.
*   **R5: Configuration Management:**
    *   Azure credentials should be primarily loaded from `.env` via `src.core.config.settings`.
    *   An optional `--config_file` can provide overrides or additional settings for transcription and evaluation.
    *   CLI arguments take the highest precedence.
*   **R6: Output Structure:**
    *   `main.py` must ensure a clean and predictable output directory structure within the user-specified `--output_dir`.
        *   Example: `[output_dir]/transcriptions/file1.txt`, `[output_dir]/transcriptions/file2.txt`, etc.
        *   Example: `[output_dir]/evaluations/file1_eval_report.json`, `[output_dir]/evaluations/batch_eval_report.json`.
*   **R7: Error Handling & Logging:**
    *   Implement robust error handling for file operations, API calls, and module interactions.
    *   Use structured logging throughout `main.py` and ensure called modules also log appropriately.
    *   Failures in one part of the pipeline (e.g., evaluation) should not necessarily halt other parts if separable (e.g., transcriptions might still be valuable).

### Non-Functional Requirements

*   **R8: Modularity:** Core logic for transcription and evaluation should remain in their respective modules/scripts. `main.py` focuses on orchestration.
*   **R9: Reusability:** The refactored transcription and evaluation modules should be reusable components.
*   **R10: Clarity:** The CLI for `main.py` should be clear, with helpful messages and well-documented arguments.
*   **R11: Extensibility:** The orchestration design should allow for future additions, like supporting different ASR services or evaluation metrics, with reasonable effort.

## 4. Proposed Technical Design

1.  **`main.py` Structure:**
    *   Argument parsing using `argparse`.
    *   Configuration loading logic (environment variables, optional config file, CLI overrides).
    *   Main conditional block: if `input_path` is file -> `run_single_file_pipeline()`, else -> `run_batch_pipeline()`.
    *   `run_single_file_pipeline()` function:
        *   Calls transcription service for the file.
        *   Handles output saving.
        *   If evaluation is requested, prepares data and calls evaluation function.
    *   `run_batch_pipeline()` function:
        *   Scans input directory for audio files.
        *   Iterates, calling transcription service for each.
        *   Handles output saving for each transcription.
        *   After all transcriptions, consolidates hypotheses.
        *   If evaluation is requested, calls evaluation function with consolidated data.
2.  **Refactoring `scripts/transcribe_azure_cli.py`:**
    *   Its core transcription logic (likely within its `main()` or a helper function calling `AzureSpeechService`) needs to be extracted into a callable function, e.g., `transcribe_audio_file(audio_path, azure_config) -> TranscriptionResult` and `transcribe_directory(dir_path, azure_config, recursive, extensions) -> BatchTranscriptionResult`.
    *   The CLI argument parsing and direct console output parts might remain for standalone use of the script but won't be used when called from `main.py`.
3.  **Refactoring `scripts/evaluate_transcriptions.py`:**
    *   This script already has `run_evaluation()` and `write_json_report()`, which seem well-suited for programmatic use. Verify that they can be imported and used directly without issues.
4.  **Configuration Handling:**
    *   A dedicated module or class (e.g., in `src.core`) could manage the hierarchical loading of configurations (defaults, .env, config file, CLI args).
5.  **State Management (for Batch):**
    *   For batch processing, simple iteration might suffice initially. For more complex scenarios (e.g., resumable jobs, detailed progress), a dedicated state tracking mechanism or class could be introduced. For this iteration, `main.py` can manage the list of files and their outcomes.

## 5. Scope

### In Scope

*   Developing `main.py` as the central orchestrator.
*   CLI for `main.py` supporting single-file and batch modes, including transcription and optional evaluation.
*   Refactoring `scripts/transcribe_azure_cli.py` to make its core transcription logic callable programmatically.
*   Ensuring `scripts/evaluate_transcriptions.py` functions are usable as intended from `main.py`.
*   Standardized output directory structure.
*   Basic configuration management (env vars, CLI args, optional config file).

### Out of Scope (for this iteration)

*   Advanced state management for resumable batch jobs.
*   A GUI for the orchestrator.
*   Support for ASR services other than Azure (unless `AzureSpeechService` is already designed for easy extension).
*   Dynamic installation of dependencies.

## 6. Dependencies & Pre-requisites

*   Existing `src.core.config`, `src.transcription.azure_speech_service`, `scripts.evaluate_transcriptions` modules.
*   Python 3.x environment with `argparse`, `os`, `pathlib`, `json`, `yaml` (if YAML config is chosen).
*   Required packages for underlying modules: `azure-cognitiveservices-speech`, `jiwer`, `python-dotenv`.

## 7. Open Questions / Future Enhancements

*   **Configuration File Format:** Decide on YAML vs. JSON for the optional config file (YAML is often more human-readable).
*   **Detailed Progress Reporting for Batch Jobs:** For very large batches, more verbose progress logging or a progress bar might be useful.
*   **Parallel Processing:** For batch transcription, explore `asyncio` or `multiprocessing` to speed up processing of multiple files, respecting API rate limits.
*   **Plugin Architecture:** For supporting other ASR services or evaluation tools in the future, a more plugin-like architecture for `main.py` could be considered. 