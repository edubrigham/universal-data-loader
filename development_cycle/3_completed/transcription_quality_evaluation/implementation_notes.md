# Implementation Notes: Transcription Quality Evaluation

## Progress Log

- **Initial Setup:** Created `scripts/evaluate_transcriptions.py` with basic structure.
- **Argparse:** Implemented CLI argument parsing for inputs, output file, and log level.
- **Data Loading:**
    - `load_ground_truth`: Successfully loads and parses the ground truth JSON file.
    - `load_hypotheses`: Implemented to handle both a directory of `.txt` files and a single JSON file (list or dict format).
- **Text Normalization (`normalize_text`):**
    - Lowercasing, punctuation removal (regex-based to preserve intra-word hyphens/apostrophes), contraction expansion, and whitespace normalization are implemented.
    - `num2words` integration was considered but deferred as `jiwer`'s default normalization or direct comparison of normalized strings often suffices. The dependency was added to `requirements.txt` for potential future use.
- **Metrics Calculation (`calculate_detailed_metrics` - formerly `calculate_wer_cer`):
    - Initially used `jiwer.wer()` and `jiwer.cer()` directly after issues with `compute_measures().get('cer')`.
    - Refactored to `calculate_detailed_metrics` to use `jiwer.compute_measures()` for H, S, D, I counts, and `jiwer.cer()` for CER. This provides the necessary details for comprehensive global error rates.
    - WER is now calculated from `(S+D+I) / (H+S+D)`.
    - Robust handling for empty strings and potential NaN/errors from `jiwer` implemented.
- **Core Logic (`run_evaluation`):
    - Iterates through hypotheses, matches with ground truth.
    - Calls normalization and `calculate_detailed_metrics`.
    - Aggregates total H, S, D, I, and GT words for accurate global rate calculation.
    - Constructs the specified JSON output structure with `global_metrics` and `per_file_results`.
- **Reporting:**
    - `print_console_report`: Updated to show new global metrics (Overall WER%, S% D%, I% rates, total counts, Avg CER%) and per-file WER%/CER% highlights.
    - `write_json_report`: Implemented to dump the detailed structured results to a JSON file. `ensure_ascii=False` added for correct UTF-8 output.
    - CSV reporting was removed in favor of the more comprehensive JSON format.
- **Testing:** Iterative testing with sample data (`ground_truth_transcriptions.json`, `hypotheses_azure_test.json`) confirmed correct calculations and output format.

## Technical Decisions & Rationales

- **Metrics Library:** Stuck with `jiwer` due to its wide use and comprehensive metrics. The issue with `compute_measures().get('cer')` returning `None` was worked around by using `jiwer.cer()` directly for CER and `compute_measures()` for the detailed counts needed for WER breakdown.
- **Output Format:** Shifted from CSV to a structured JSON output. This provides much richer data (including original/normalized texts, raw per-file metrics) and is better suited for programmatic consumption or frontend display, aligning with the user's final request.
- **Global Error Rates Calculation:** Ensured that global WER and its components (Insertion Rate, Deletion Rate, Substitution Rate) are calculated based on the *sum of total errors* and *sum of total ground truth words* across all files, not by averaging per-file rates. This provides a more accurate overall measure.
- **Normalization:** Implemented a solid baseline normalization. Kept it within the main script for now; can be refactored if it grows significantly more complex.

## TODO / Future Considerations

- **(Optional) More Advanced Normalization:** If specific project needs arise (e.g., handling specific disfluencies, more complex number/date formats not covered by `jiwer`'s internal processing), the `normalize_text` function can be further enhanced. Consider a configurable normalization pipeline.
- **(Optional) Unit Tests:** While manual testing was performed, formal unit tests could be added for `normalize_text`, `calculate_detailed_metrics`, and data loading functions to ensure long-term robustness, especially if the script undergoes further modifications.
- **(Optional) Alternative Hypothesis Formats:** While the current hypothesis loader is flexible, support for other specific ASR output formats could be added if needed.

## Key Learnings / Issues Encountered

- **`jiwer.compute_measures()` CER:** The `cer` key was not reliably present or was `None` in the output of `jiwer.compute_measures()` in the testing environment. Switching to `jiwer.cer()` for CER and `jiwer.compute_measures()` primarily for word-level H,S,D,I counts resolved this and provided the necessary granularity.
- **JSON Output Detail:** The requirement for a detailed JSON output for potential frontend use was a key driver in the final structure of `results_data` and the reporting functions.
- **Importance of Aggregate Counts for Global Rates:** Realized early that averaging per-file WERs is not the correct way to get a true global WER. The implementation correctly uses total error counts and total ground truth words.

### Date: {{YYYY-MM-DD}}

### Progress:
- Initial project structure for the evaluation script (`scripts/evaluate_transcriptions.py`) created.
- Basic argument parsing implemented using `argparse`.
- Data loading functions (`load_ground_truth`, `load_hypotheses`) implemented with support for JSON and directory inputs.
- Placeholder text normalization (`normalize_text`) and metrics calculation (`calculate_wer_cer`) functions created.
- Reporting functions (`print_console_report`, `write_csv_report`, `write_json_report`) implemented.
- Core evaluation logic in `run_evaluation()` connects these pieces.
- `main()` function orchestrates the script flow and handles output based on arguments.

### Technical Decisions:
- **Metrics Library**: `jiwer` is the chosen library. A placeholder is used for now, with a TODO to fully integrate and add to dependencies.
- **Hypothesis Input**: `load_hypotheses` supports both a directory of `.txt` files and a JSON file (either a list of objects or a direct filename-to-text mapping).
- **Filename Matching**: Basename of files (e.g., `audio.wav`) is used for matching ground truth and hypotheses to ensure consistency if paths or extensions differ.
- **Output Logic in `main`**: `run_evaluation` returns data. `main` handles all reporting (console and file) to decouple logic. If an `output_file` is specified with `output_format='console'`, the script defaults to writing a CSV file to the specified path *in addition* to console output, as per spec recommendation (Console + CSV).
- **Error Handling**: Basic `try-except` blocks for file operations and JSON parsing. `run_evaluation` returns `None` on critical load failures.

### Challenges Encountered:
- (Record any challenges here, e.g., ambiguity in spec, library issues, complex data structures)
- Initial linter errors due to newline characters in string literals within the `edit_file` tool's `code_edit` parameter required careful correction and re-application of the script.

### TODOs / Next Steps:
- Fully integrate `jiwer` for metrics calculation and add it to `requirements.txt` / `pyproject.toml`.
- Expand `normalize_text` with more robust normalization rules (e.g., number normalization, more comprehensive punctuation handling, contraction expansion) as per `design.md` and `task_list.md`.
- Create example `ground_truth_transcriptions.json` and hypothesis data for testing.
- Implement unit tests for all major components (data loading, normalization, metrics calculation, core logic).
- Add comprehensive docstrings and comments following project guidelines.
- Test thoroughly with various input scenarios (e.g., missing files, empty files, mismatched data).
- Refine logging for clarity and appropriate levels.
- Create `README.md` for the script itself in the `scripts/` directory.

### Deviations from Plan:
- (Note any deviations from `spec.md` or `design.md` and the reasons)

--- 