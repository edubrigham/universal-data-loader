# Task List: Transcription Quality Evaluation

This task list outlines the steps to implement the Transcription Quality Evaluation feature.

## Phase 1: Initial Setup and Core Logic

- [X] **Project Setup & Feature Scaffolding (Manual by User/AI)**
    - [X] Create feature branch (if applicable).
    - [X] Create `development_cycle/2_inprogress/transcription_quality_evaluation/` directory.
    - [X] Populate with initial `README.md`, `spec.md`, `design.md` (derived from planning).

- [X] **Dependency Management**
    - [X] Add `jiwer` to `requirements.txt` for WER/CER calculation.
    - [X] Consider and add `num2words` to `requirements.txt` (though direct usage was deferred).

- [X] **Argument Parsing (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement CLI argument parsing using `argparse`.
    - [X] Arguments:
        - [X] `--ground_truth_file` (required)
        - [X] `--hypotheses_input` (required)
        - [X] `--output_file` (optional, for JSON report)
        - [X] `--log_level` (optional, default INFO)

- [X] **Data Loading (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement `load_ground_truth()` function:
        - [X] Load from JSON file.
        - [X] Handle file errors and JSON parsing errors.
        - [X] Return `Dict[str, str]` (filename -> text).
    - [X] Implement `load_hypotheses()` function:
        - [X] Support loading from a directory of `.txt` files.
        - [X] Support loading from a single JSON file (list or dict format).
        - [X] Handle file errors and JSON parsing errors.
        - [X] Return `List[Dict[str, str]]` (list of {filename, text} dicts).

- [X] **Text Normalization (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement `normalize_text()` function:
        - [X] Lowercase text.
        - [X] Expand common English contractions.
        - [X] Remove punctuation (preserving intra-word hyphens/apostrophes with regex).
        - [X] Normalize whitespace.

- [X] **Metrics Calculation (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement `calculate_detailed_metrics()` function (renamed from `calculate_wer_cer`):
        - [X] Use `jiwer.compute_measures()` for hits, substitutions, deletions, insertions.
        - [X] Calculate `ground_truth_words`.
        - [X] Calculate WER based on S, D, I counts and ground_truth_words.
        - [X] Use `jiwer.cer()` for CER.
        - [X] Handle `ImportError` for `jiwer`.
        - [X] Handle potential exceptions/NaN from `jiwer` and return structured error/default values.
        - [X] Return dict: `{wer, cer, hits, substitutions, deletions, insertions, ground_truth_words}`.

- [X] **Core Evaluation Logic (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement `run_evaluation()` function:
        - [X] Orchestrate data loading, normalization, and metrics calculation.
        - [X] Match hypotheses to ground truth using filenames.
        - [X] Aggregate total H, S, D, I, GT_words counts across all files.
        - [X] Calculate global WER%, S%, D%, I% rates and average CER%.
        - [X] Construct `results_data` dict with `global_metrics` and `per_file_results`.
        - [X] Include original/normalized texts and raw_metrics in `per_file_results`.
        - [X] Handle missing ground truth or hypothesis entries gracefully.
        - [X] Handle errors from `calculate_detailed_metrics` for individual files.

## Phase 2: Reporting and Refinements

- [X] **Reporting (`scripts/evaluate_transcriptions.py`)**
    - [X] Implement `print_console_report()`:
        - [X] Display global metrics (Overall WER%, S% D%, I% rates, total counts, Avg CER%).
        - [X] Display per-file WER% and CER% highlights.
    - [X] Implement `write_json_report()`:
        - [X] Write the detailed `results_data` (global and per-file) to a JSON file.
        - [X] Ensure pretty printing (indent) and UTF-8 encoding.
    - [X] Remove `write_csv_report()` and related CLI options.

- [X] **Logging (`scripts/evaluate_transcriptions.py`)**
    - [X] Integrate `logging` module throughout the script.
    - [X] Ensure log level is configurable via CLI.

- [X] **Main Function (`scripts/evaluate_transcriptions.py`)**
    - [X] Set up `main()` to call argument parser and `run_evaluation()`.
    - [X] Call reporting functions based on CLI arguments (console always, JSON if `--output_file` provided).

## Phase 3: Testing and Documentation

- [X] **Testing (Manual/Iterative)**
    - [X] Create/use sample ground truth JSON (`evaluation-data/ground_truth_transcriptions.json`).
    - [X] Create/use sample hypothesis data (`evaluation-data/hypotheses_azure_test.json` from Azure outputs).
    - [X] Run the script with various inputs and options.
    - [X] Verify console output and JSON report against expected values.
    - [X] Test edge cases (e.g., empty files, missing matches, `jiwer` errors).

- [X] **Docstrings and Comments (`scripts/evaluate_transcriptions.py`)**
    - [X] Add comprehensive docstrings to all functions and modules.
    - [X] Add comments for complex or non-obvious code sections.

- [X] **Update Feature Documentation (Manual by User/AI)**
    - [X] Update `README.md` in the feature directory with final usage, I/O formats, and capabilities.
    - [X] Update `spec.md` with final specifications and output formats.
    - [X] Update `design.md` with final component design and data flow.
    - [X] Update this `task_list.md` to mark completed tasks.
    - [X] Update `implementation_notes.md` with final decisions and learnings.

## Phase 4: Final Review (Optional)
- [ ] Code review (if applicable).
- [ ] User acceptance testing (if applicable). 