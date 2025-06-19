# Feature Specification: Transcription Quality Evaluation

## 1. Introduction
This document specifies the functionality and technical scope for the Transcription Quality Evaluation feature. The goal is to provide a reliable tool for measuring the accuracy of ASR transcriptions against ground truth data.

## 2. Functionality

### 2.1. Core Functionality
- **Data Input:**
    - **Ground Truth:** Load from a specified JSON file. Each entry must contain at least `audio_file_name` (used as a key, basename of the audio file) and `ground_truth_text`.
    - **Hypotheses:** Load from a specified path, which can be:
        - A directory containing individual hypothesis text files (e.g., `.txt`), where each filename matches an `audio_file_name` from the ground truth.
        - A single JSON file containing hypotheses. This JSON can be a list of objects (each with `audio_file_name` and `text`) or a dictionary mapping `audio_file_name` to `text`.
- **Text Normalization:**
    - Before comparison, both ground truth and hypothesis texts undergo normalization. This includes:
        - Lowercasing.
        - Expansion of common English contractions.
        - Removal of punctuation (while preserving intra-word hyphens/apostrophes).
        - Normalization of whitespace to single spaces.
- **Metrics Calculation:**
    - For each ground truth/hypothesis pair, calculate:
        - Word Error Rate (WER).
        - Character Error Rate (CER).
        - Detailed word error counts: hits, substitutions, deletions, insertions.
        - Number of words in the ground truth text.
    - All metrics are calculated using the `jiwer` library.
- **Aggregation:**
    - Calculate global metrics across all successfully evaluated file pairs:
        - Overall WER percentage (based on total S, D, I counts and total ground truth words).
        - Overall Insertion Rate percentage.
        - Overall Substitution Rate percentage.
        - Overall Deletion Rate percentage.
        - Total counts for ground truth words, hits, S, D, I.
        - Average CER percentage (arithmetic mean of per-file CERs).
    - Track counts for total files evaluated and files missing ground truth.

### 2.2. Command-Line Interface (CLI)
- The feature is implemented as a Python script: `scripts/evaluate_transcriptions.py`.
- **Key Arguments:**
    - `--ground_truth_file <path>`: (Required) Path to the ground truth JSON file.
    - `--hypotheses_input <path>`: (Required) Path to the hypotheses directory or JSON file.
    - `--output_file <path>`: (Optional) Path to save the detailed JSON report. If not provided, results are only printed to the console summary.
    - `--log_level <LEVEL>`: (Optional) Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO.

### 2.3. Output and Reporting
- **JSON Report File (if `--output_file` is specified):**
    - A single JSON file containing two main keys:
        - `global_metrics`: An object with all aggregated metrics (WER%, S% D%, I% rates, total counts, average CER%, files evaluated, files missing GT).
        - `per_file_results`: A list, where each item is an object representing an evaluated audio file. Each object includes:
            - `audio_file_name`
            - `wer_percentage`, `cer_percentage`
            - `status` (e.g., 'evaluated', 'missing_ground_truth', 'error_in_metrics')
            - `ground_truth_original`, `hypothesis_original` (the texts as loaded)
            - `ground_truth_normalized`, `hypothesis_normalized` (the texts after normalization)
            - `raw_metrics`: A sub-object with the direct outputs from `calculate_detailed_metrics` (WER, CER, and counts for H, S, D, I, GT words for that specific file).
- **Console Output:**
    - A summary of the `global_metrics`.
    - A condensed list of `per_file_results` showing `audio_file_name`, `WER%`, and `CER%`.
    - Log messages indicating progress, warnings, and errors, controlled by `--log_level`.

## 3. Technical Scope
- **Language:** Python.
- **Primary Libraries:** `jiwer` (for metrics), `argparse` (for CLI), `json`, `logging`, `pathlib`, `re`.
- **Error Handling:** The script includes error handling for file operations, JSON parsing, missing data, and issues during metrics calculation (e.g., if `jiwer` encounters an problem).
- **Extensibility:** The text normalization function is designed to be extensible if more rules are needed in the future.

## 4. Out of Scope (for this iteration)
- Direct audio file processing (the script works with pre-existing text transcriptions).
- Advanced statistical analysis beyond the calculated metrics.
- A graphical user interface (GUI) – output is CLI and JSON file.
- Real-time evaluation.

## 5. UI/Output Format (Final)
- The primary structured output is the JSON file described in section 2.3. This format is designed for machine readability and potential use in frontends or further data analysis pipelines.
- The console output provides a human-readable summary for quick checks. 