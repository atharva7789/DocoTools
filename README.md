# DocoTools — Online PDF & Document Utility Platform

A modern Flask-based mini project for an end-to-end DevOps demonstration.

## Features

- Merge PDF
- Split PDF
- Compress PDF
- JPG → PDF
- PDF → JPG
- PDF → Word
- PDF → PowerPoint
- PDF → Excel
- PowerPoint → PDF
- Excel → PDF
- AI Summarizer
- Temporary file processing
- Delete your file
- Docker
- GitHub Actions CI
- Automated tests

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5002

## Docker

```bash
docker compose up --build
```

## DevOps flow

GitHub → GitHub Actions → pytest → Docker build → deployment stage.

## Privacy note

This educational implementation creates a unique temporary job directory for each request. Uploaded source files are removed after successful processing, while the generated result remains until the user deletes the job or the server removes it.
