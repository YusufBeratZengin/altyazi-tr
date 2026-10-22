# Security Policy

## Offline Privacy Architecture

`altyazi-tr` is engineered to process media and transcripts strictly offline:
- **Zero Network Egress**: The package makes no outbound HTTP/API calls during transcription, layout, or rendering.
- **Local Model Execution**: Local inference is performed entirely on your machine via faster-whisper/CTranslate2. The CLI adapter operates with `local_files_only=True` and never initiates automatic model downloads.
- **Local Artifacts**: Media files, subtitles, and `--report json` diagnostics remain exclusively on your local disk.

## Supported Versions

| Version | Supported |
| --- | --- |
| 0.1.x | :white_check_mark: |
| < 0.1.0 | :x: |

## Reporting a Vulnerability

If you discover a security vulnerability or potential privacy issue in `altyazi-tr`, please report it privately:

1. Open a private security advisory through GitHub:
   [https://github.com/YusufBeratZengin/altyazi-tr/security/advisories/new](https://github.com/YusufBeratZengin/altyazi-tr/security/advisories/new)
2. Include a detailed description of the vulnerability, reproduction steps, and potential impact.
3. Please do **NOT** open public issues or attach private audio/video recordings. Use synthetic dummy files to reproduce issues.

We take security and privacy reports seriously and will acknowledge reports promptly.
