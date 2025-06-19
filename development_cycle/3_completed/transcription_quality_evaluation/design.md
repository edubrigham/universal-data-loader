# Design Document: Transcription Quality Evaluation

## 1. Architecture Overview

The Transcription Quality Evaluation feature is implemented as a standalone Python script: `scripts/evaluate_transcriptions.py`. This script can be invoked from the command line and is designed to be self-contained in its core logic, relying on the `jiwer` library for metrics calculation.

**Key Architectural Principles:**
- **Modularity:** Functions are organized for specific tasks (data loading, normalization, metrics calculation, reporting).
- **Clarity:** Code is commented, and function names are descriptive.
- **Robustness:** Includes error handling for I/O, data parsing, and potential issues during metric calculation.
- **Configurability:** Uses `argparse` for command-line arguments (input/output paths, log level).

## 2. Components

1.  **Argument Parser (`argparse` setup in `main()`):**
    *   Responsibilities: Define and parse command-line arguments (`--ground_truth_file`, `--hypotheses_input`, `--output_file`, `--log_level`).
    *   Interactions: Passes parsed arguments to the main evaluation logic.

2.  **Data Loading Module:**
    *   `load_ground_truth(file_path: str) -> Dict[str, str]`: Reads a JSON file, validates its structure, and returns a dictionary mapping `audio_file_name` (basename) to `ground_truth_text`.
    *   `load_hypotheses(input_path_str: str) -> List[Dict[str, str]]`: Loads hypotheses from either a directory of `.txt` files or a single JSON file (supporting list or dict formats). Returns a list of dictionaries, each with `audio_file_name` (basename) and `text`.
    *   Error handling for file not found, JSON decoding errors, and incorrect formats.

3.  **Text Normalization Module (`normalize_text(text: str) -> str`):**
    *   Responsibilities: Applies a series of normalization steps to a given text string to prepare it for comparison.
    *   Steps:
        1.  Convert to lowercase.
        2.  Expand common English contractions.
        3.  Remove punctuation (using regex to preserve intra-word hyphens/apostrophes).
        4.  Normalize whitespace (multiple spaces/tabs/newlines to a single space, strip leading/trailing).
    *   This function is called for both ground truth and hypothesis texts.

4.  **Metrics Calculation Module (`calculate_detailed_metrics(ground_truth: str, hypothesis: str) -> Dict[str, Any]`):**
    *   Responsibilities: Calculate WER, CER, and detailed word error counts using `jiwer`.
    *   Uses `jiwer.compute_measures()` for hits, substitutions, deletions, insertions.
    *   Calculates `ground_truth_words = hits + substitutions + deletions`.
    *   Calculates `wer = (substitutions + deletions + insertions) / ground_truth_words` (with handling for `ground_truth_words == 0`).
    *   Uses `jiwer.cer()` for Character Error Rate.
    *   Handles `ImportError` if `jiwer` is not found.
    *   Handles potential exceptions during `jiwer` calls and ensures non-negative, valid numeric outputs (or NaN on error).
    *   Returns a dictionary: `{ 'wer': wer, 'cer': cer, 'hits': hits, 'substitutions': s, 'deletions': d, 'insertions': i, 'ground_truth_words': ground_truth_words }`.

5.  **Core Evaluation Logic (`run_evaluation(ground_truth_file: str, hypotheses_input: str) -> Optional[Dict[str, Any]]`):**
    *   Orchestrates the entire evaluation process.
    *   Calls data loading functions.
    *   Iterates through hypotheses, finds matching ground truth using `audio_file_name`.
    *   For each pair:
        *   Calls `normalize_text` for both GT and Hyp.
        *   Calls `calculate_detailed_metrics`.
    *   Aggregates total counts (hits, S, D, I, ground_truth_words) and total CER sum across all evaluated files.
    *   Calculates global metrics (Overall WER%, S% D%, I% rates, Average CER%) based on these aggregate counts.
    *   Constructs the final `results_data` dictionary with `global_metrics` and `per_file_results` (including original/normalized texts and raw per-file metrics).
    *   Handles cases where ground truth or hypotheses are not found or if metrics calculation fails for a file.

6.  **Reporting Module:**
    *   `print_console_report(results: Dict[str, Any])`: Prints a human-readable summary of global metrics and per-file WER/CER highlights to the console.
    *   `write_json_report(results: Dict[str, Any], output_file_path: str)`: Writes the full `results_data` dictionary to a specified JSON file, formatted with an indent for readability.

7.  **Logging (`logging` module):**
    *   Used throughout the script for INFO, DEBUG, WARNING, ERROR messages.
    *   Log level is configurable via CLI argument.

## 3. Data Flow Diagram

```mermaid
graph LR
    A[CLI Arguments: --ground_truth_file, --hypotheses_input, --output_file, --log_level] --> B(main_function);

    B --> C{run_evaluation};
    C --> D[load_ground_truth];
    C --> E[load_hypotheses];

    D --> F[GroundTruthMap: Dict[filename, gt_text]];
    E --> G[HypothesesList: List[Dict[filename, hyp_text]]];

    C -- For each hypo in G --> H{Match GT from F};
    H -- Found --> I[normalize_text GT];
    H -- Found --> J[normalize_text Hyp];
    I --> K[Normalized GT Str];
    J --> L[Normalized Hyp Str];

    K --> M{calculate_detailed_metrics};
    L --> M;
    M --> N[PerFileMetrics: Dict[wer, cer, h,s,d,i, gt_words]];

    C -- Aggregates N --> O[GlobalMetrics: Dict[Overall WER%, Rates%, Counts]];
    C -- Collects N & original/normalized texts --> P[PerFileResultsList];

    O --> Q[FinalResultsJSON_Object];
    P --> Q;

    C --> R{print_console_report};
    Q --> R;
    C -- If --output_file --> S{write_json_report};
    Q --> S;

    S --> T([output_report.json]);
    R --> U([Console Output]);
```

## 4. Component Interactions

- The `main` function parses CLI args and calls `run_evaluation`.
- `run_evaluation` orchestrates calls to `load_ground_truth`, `load_hypotheses`.
- For each matched pair, `run_evaluation` calls `normalize_text` on both strings, then passes the normalized strings to `calculate_detailed_metrics`.
- `calculate_detailed_metrics` uses `jiwer` internally.
- `run_evaluation` accumulates results from `calculate_detailed_metrics` to build the final `global_metrics` and `per_file_results` data structure.
- This final data structure is passed to `print_console_report` and (if specified) `write_json_report`.

## 5. Error Handling
- **File I/O:** `FileNotFoundError` is caught and logged if input files/directories are not found.
- **JSON Parsing:** `json.JSONDecodeError` is caught and logged for malformed JSON files.
- **Data Validation:** Basic checks for expected structure in ground truth and hypothesis JSON.
- **Missing Data:** Warnings are logged if ground truth is missing for a hypothesis, or if hypotheses are missing.
- **Metrics Calculation:** `ImportError` for `jiwer` is handled. Other exceptions during `jiwer` calls are caught, and the affected file's metrics are marked appropriately (e.g. NaN, status 'error_in_metrics'), allowing the script to continue with other files.
- **Logging:** Different log levels provide varying degrees of detail for diagnostics.

## 6. UI Mockups / Output Format Examples

This section is superseded by the detailed output format described in `spec.md` (Section 2.3. Output and Reporting) and `README.md` (Section 2. Key Requirements - Output), which accurately reflects the final JSON structure and console summary.

**Key JSON Structure:**
```json
{
  "global_metrics": {
    "wer_percentage": 5.88,
    "insertion_rate_percentage": 0.0,
    "substitution_rate_percentage": 5.88,
    "deletion_rate_percentage": 0.0,
    "total_ground_truth_words": 34,
    // ... other global counts and rates
  },
  "per_file_results": [
    {
      "audio_file_name": "some_file.wav",
      "wer_percentage": 13.33,
      "cer_percentage": 3.16,
      "status": "evaluated",
      "ground_truth_original": "...",
      "hypothesis_original": "...",
      "ground_truth_normalized": "...",
      "hypothesis_normalized": "...",
      "raw_metrics": {
        "wer": 0.1333,
        "cer": 0.0316,
        "hits": 13,
        "substitutions": 2,
        "deletions": 0,
        "insertions": 0,
        "ground_truth_words": 15
      }
    }
    // ... other files
  ]
}
```

**Console Summary Example:**
```text
INFO - --- Evaluation Report Summary ---
INFO -
--- Global Metrics ---
INFO - Total Files Evaluated: 2
INFO - Files Missing Ground Truth: 0
INFO - Total Ground Truth Words: 34
INFO -   Total Hits: 32
INFO -   Total Substitutions: 2 (5.88%)
INFO -   Total Deletions: 0 (0.00%)
INFO -   Total Insertions: 0 (0.00%)
INFO - Overall WER: 5.88%)
INFO - Average CER: 1.58%)
INFO -
--- Per-File WER/CER Highlights ---
INFO - Urgences9.wav: WER=13.33%, CER=3.16%
INFO - Soins Continus et Palliatifs10.wav: WER=0.00%, CER=0.00%
INFO - --- End of Report Summary ---
``` 