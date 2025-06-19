# Azure Speech-to-Text Integration - README

## Goal

Implement functionality to transcribe audio files using the Azure Speech-to-Text service.

## Key Requirements

*   The application must be able to authenticate with the Azure Speech service using configured credentials (API key, region).
*   The application must accept an audio file path (e.g., WAV format) as input.
*   The application must send the audio file to the Azure Speech-to-Text service, specifically targeting a custom speech model if an endpoint ID is provided.
*   The application must receive and process the transcription text from the service.
*   The application must handle and report errors gracefully (e.g., authentication failure, invalid file, service errors, no match, cancellation).
*   Configuration (API key, region, custom model endpoint ID) must be managed securely, for example, via environment variables loaded from a `.env` file.
*   The implementation should primarily use the Azure Speech SDK.

## Target Audience

*   **Developers:** Integrating this feature into a larger application.
*   **End Users:** Users of an application that incorporates this feature, who need to convert spoken audio into text.

## Open Questions

*   What are the expected peak and average loads for transcription requests? (To consider rate limits and potential scaling needs).
*   Are there specific audio formats beyond WAV that need to be supported initially? (The SDK might require GStreamer or other dependencies for certain compressed formats).
*   What is the desired user experience for reporting transcription progress or long-running transcriptions?
*   Are there specific requirements for storing or logging transcription results beyond returning them to the caller? 