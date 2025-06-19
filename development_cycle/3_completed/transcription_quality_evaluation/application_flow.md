# Application Flow: Transcription Quality Evaluation

This document outlines the end-to-end application flow for preparing data, performing transcriptions, and evaluating transcription quality.

## Overall Workflow Stages

1.  **Data Preparation (Ground Truth & Audio):** Ensuring audio files and their corresponding correct transcriptions are available.
2.  **Hypothesis Generation (ASR Transcription):** Using an Automated Speech Recognition (ASR) service to transcribe the audio files.
3.  **Evaluation:** Comparing the ASR-generated hypotheses against the ground truth using the evaluation script.

## Detailed Application Flow

**Stage 1: Data Preparation (Ground Truth & Audio)**

1.  **Audio Files Collection:**
    *   **Source:** Audio files (e.g., `.wav` format) that need to be transcribed and evaluated are collected.
    *   **Location:** Typically stored in a directory like `evaluation-data/` (e.g., `evaluation-data/Urgences9.wav`, `evaluation-data/Allergologie1.wav`, etc.).

2.  **Ground Truth Creation/Curation:**
    *   **Process:** For each audio file, a highly accurate, human-verified transcription (the "ground truth") is created or curated.
    *   **Format:** These ground truths are consolidated into a single JSON file.
    *   **File:** `evaluation-data/ground_truth_transcriptions.json`
    *   **Structure (as implemented):** A JSON list, where each object contains:
        *   `audio_file_name`: The exact filename of the corresponding audio file (e.g., `"Urgences9.wav"`).
        *   `ground_truth_text`: The human-verified correct transcription text (e.g., `"Y a-t-il des programmes éducatifs..."`).
    *   **Example Snippet from `ground_truth_transcriptions.json`:**
        ```json
        [
          {
            "audio_file_name": "Urgences9.wav",
            "ground_truth_text": "Y a-t-il des programmes éducatifs sur les premiers secours proposés par le service des urgences?"
          },
          // ... other entries
        ]
        ```

**Stage 2: Hypothesis Generation (ASR Transcription)**

1.  **Select ASR Service & Configuration:**
    *   The primary ASR service used in this project is Azure Cognitive Speech Services.
    *   Configuration details (API key, region, custom model endpoint if any) are required.

2.  **Transcribe Audio Files:**
    *   **Tool:** The `scripts/transcribe_azure_cli.py` script is used to send audio files to the Azure ASR service.
    *   **Input:** An individual audio file path (e.g., `evaluation-data/Urgences9.wav`).
    *   **Process (per audio file executed by user/another script):
        ```bash
        python scripts/transcribe_azure_cli.py \
            --input_path "evaluation-data/Urgences9.wav" \
            --output_path "temp_azure_outputs/Urgences9.txt" \
            --speech_key "YOUR_AZURE_SPEECH_KEY" \
            --speech_region "YOUR_AZURE_REGION" \
            # --endpoint_id "YOUR_CUSTOM_MODEL_ENDPOINT_ID" # Optional
        ```
    *   **Output (per audio file):** The ASR service returns the transcribed text, which `transcribe_azure_cli.py` saves to a temporary text file (e.g., in `temp_azure_outputs/Urgences9.txt`). The content is the raw hypothesis text.

3.  **Consolidate Hypotheses into a Single JSON File:**
    *   **Process:** The individual hypothesis text files (from `temp_azure_outputs/`) are manually or programmatically consolidated into a single JSON file structured for the evaluation script.
    *   **File:** For example, `evaluation-data/hypotheses_azure_test.json` (or a more comprehensive file like `evaluation-data/all_hypotheses.json`).
    *   **Structure (as implemented and expected by evaluation script):** A JSON list, where each object contains:
        *   `audio_file_name`: The filename of the original audio (e.g., `"Urgences9.wav"`).
        *   `text`: The hypothesis text transcribed by the ASR service (e.g., `"YAT il des programmes éducatifs..."`).
    *   **Example Snippet from `hypotheses_azure_test.json`:**
        ```json
        [
            {
                "audio_file_name": "Urgences9.wav",
                "text": "YAT il des programmes éducatifs sur les premiers secours proposés par le service des urgences."
            },
            // ... other entries for other transcribed files
        ]
        ```
    *   *Note: The evaluation script also supports a dictionary format for this hypotheses JSON and can directly read a directory of .txt files, but a consolidated JSON like the list above is a common pattern used.* 

**Stage 3: Evaluation**

1.  **Run Evaluation Script:**
    *   **Tool:** `scripts/evaluate_transcriptions.py`.
    *   **Inputs (as specified in its arguments):
        *   `--ground_truth_file`: Path to the consolidated ground truth JSON (e.g., `"evaluation-data/ground_truth_transcriptions.json"`).
        *   `--hypotheses_input`: Path to the consolidated hypotheses JSON (e.g., `"evaluation-data/hypotheses_azure_test.json"`) OR path to a directory of hypothesis `.txt` files.
        *   `--output_file`: (Optional) Path to save the detailed JSON evaluation report (e.g., `"evaluation_results_detailed.json"`).
        *   `--log_level`: (Optional) Verbosity of console logging.
    *   **Command Example:**
        ```bash
        python scripts/evaluate_transcriptions.py \
            --ground_truth_file "evaluation-data/ground_truth_transcriptions.json" \
            --hypotheses_input "evaluation-data/hypotheses_azure_test.json" \
            --output_file "evaluation_results_detailed.json" \
            --log_level INFO
        ```

2.  **Evaluation Script Processing (Internal Flow - High Level):**
    *   **Load Data:** Ground truths and hypotheses are loaded into memory.
    *   **Match Pairs:** For each hypothesis, the script attempts to find a corresponding ground truth entry based on `audio_file_name`.
    *   **Normalize Texts:** Both ground truth and hypothesis texts for matched pairs are normalized (lowercase, punctuation removal, contraction expansion, etc.).
    *   **Calculate Metrics:** For each normalized pair, `jiwer` is used to calculate WER, CER, and detailed error counts (hits, substitutions, deletions, insertions).
    *   **Aggregate Results:** Total error counts and total ground truth words are summed up across all evaluated files.
    *   **Calculate Global Rates:** Overall WER%, Insertion%, Substitution%, Deletion% rates, and average CER% are computed from these aggregate totals.

3.  **Output Generation:**
    *   **Console Output:** A summary of global metrics and per-file WER/CER highlights is printed to the console.
    *   **JSON Report File:** If `--output_file` was specified, a detailed JSON file is created. This file contains:
        *   `global_metrics`: All aggregated scores and counts.
        *   `per_file_results`: A list detailing metrics, original/normalized texts, and status for each processed file.

## Summary Diagram of Key Files and Scripts

```mermaid
graph TD
    subgraph AA [Audio & Manual Ground Truth]
        A1["`evaluation-data/*.wav` (Audio Files)"]
        A2["`evaluation-data/ground_truth_transcriptions.json` (Curated GT Text)"]
    end

    subgraph BB [ASR Transcription by Azure]
        B1["`scripts/transcribe_azure_cli.py`"] -- Processes each .wav --> B2["`temp_azure_outputs/*.txt` (Individual Hypotheses)"];
        B2 -- Consolidated into --> B3["`evaluation-data/hypotheses_XYZ.json` (All Hypotheses)"];
    end
    
    A1 --> B1;

    subgraph CC [Evaluation]
        C1["`scripts/evaluate_transcriptions.py`"] -- Reads --> A2;
        C1 -- Reads --> B3;
        C1 -- Generates --> C2["Console Summary"];
        C1 -- Generates --> C3["`evaluation_results_XYZ.json` (Detailed Report)"];
    end
```

This flow clarifies that the evaluation script (`evaluate_transcriptions.py`) is the final step, consuming pre-prepared ground truth and hypothesis files, where the hypotheses themselves are outputs from an earlier ASR transcription stage (e.g., using `transcribe_azure_cli.py` and subsequent consolidation). 