# 🛡️ SentinelMind AI v2.0
> **Advanced Multimodal & Multilingual Threat, Sarcasm, Emotion, and Content Moderation System**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Transformers](https://img.shields.io/badge/NLP-Hugging%20Face%20Transformers-FFD21E.svg?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch-EE4C2C.svg?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#license)

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Setup](#-installation--setup)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone & Environment Setup](#2-clone--environment-setup)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Model Download (Optional)](#4-model-download-optional)
- [Running the Application](#-running-the-application)
  - [Running the Backend API](#running-the-backend-api)
  - [Using the Standalone Web Dashboard](#using-the-standalone-web-dashboard)
  - [Running the React Frontend](#running-the-react-frontend)
- [API Reference](#-api-reference)
  - [Endpoint: `POST /analyze`](#endpoint-post-analyze)
  - [Sample Response](#sample-response)
- [Risk Level Matrix](#-risk-level-matrix)
- [Contributing & Roadmap](#-contributing--roadmap)
- [License](#-license)

---

## 📖 Overview

**SentinelMind AI v2.0** is an intelligent, multi-layered NLP and content-safety engine developed to detect sarcasm, assess threat levels, classify complex emotions, sanitize toxic content, and determine conversational dynamics.

Unlike standard mono-lingual classifiers, SentinelMind is built to handle **multilingual text** and **code-mixed vernacular languages** common in Indian social interactions (English, Hindi, Tamil, Kannada, and code-mixed romanized variants like Hinglish, Tanglish, and Kanglish).

Additionally, SentinelMind supports **multimodal document and image ingestion**, extracting content from PDFs and images (via OCR) to deliver actionable safety metrics in real-time.

---

## ✨ Key Features

- **🌐 Multilingual & Code-Mixed Support**:
  - Automatically identifies native scripts (Devanagari, Tamil, Kannada) and romanized phonetic code-mixed sentences (e.g., *"maga ivattu office promotion happy"*).
  - Dynamic translation to English using `deep_translator` for consistent cross-lingual understanding.

- **😏 Sarcasm Detection**:
  - Context-aware detection of sarcastic and ironic patterns across multiple languages with confidence scoring.

- **🧠 Hybrid Emotion Recognition**:
  - Combines deterministic rule-based heuristic engines with state-of-the-art Transformer models (`RoBERTa-go_emotions` / `DeBERTa-v3`).
  - **Fusion Engine**: Synthesizes rule outputs and deep neural network embeddings to output high-accuracy emotion labels.

- **🚨 Threat & Illegal Activity Detection**:
  - Scans for critical security risks, violent threats, weapons, attacks, and illegal actions.

- **⚖️ Dynamic Risk Scoring**:
  - Multi-tiered risk classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) computed from threats, emotional intensity, and sarcasm indicators.

- **👥 Relationship Inference**:
  - Infers relational context between communicators (e.g., *Parent / Child*, *Friends*, *Teacher / Student*, *Close Relationship*).

- **🛡️ Extreme Profanity Filter**:
  - Automatic pattern-based redaction and masking of severe profanities.

- **📄 Multimodal Document & Image Parsing**:
  - Supports uploading `.pdf` files (extracted via `PyMuPDF`) and `.png`/`.jpg`/`.jpeg` images (extracted via Tesseract OCR).

- **📝 Smart Summarization**:
  - Extractive text summarizer generating concise previews for long inputs.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[Input: Raw Text / PDF Document / Image OCR] --> B[FastAPI Backend /analyze]
    
    subgraph Ingestion & Preprocessing
        B --> C1[PyMuPDF: PDF Text Extractor]
        B --> C2[PyTesseract: Image OCR]
        B --> C3[Text Sanitizer & Profanity Masker]
    end

    subgraph Language & Translation
        C3 --> D1[Smart Language Detector\nNative Scripts & Code-Mixed Romanized]
        D1 --> D2[Dynamic GoogleTranslator\nNon-English -> English]
    end

    subgraph Analytical Pipelines
        D2 --> E1[Multilingual Sarcasm Detector]
        D2 --> E2[Threat & Illegal Activity Scanner]
        D2 --> E3[Relationship Dynamics Classifier]
        D2 --> E4[Rule-Based Emotion Engine]
        D2 --> E5[Transformer DeBERTa/RoBERTa Emotion Pipeline]
    end

    subgraph Synthesis & Decision
        E4 & E5 --> F1[Emotion Fusion Engine]
        E1 & E2 & F1 --> F2[Risk Assessment Engine\nCRITICAL | HIGH | MEDIUM | LOW]
        D2 --> F3[Smart Summary Generator]
    end

    subgraph Client Applications
        F2 & F3 --> G1[JSON API Response]
        G1 --> H1[Standalone Glassmorphism Dashboard\nindex.html]
        G1 --> H2[React 19 Modern Web App\nfrontend/]
    end
```

---

## 💻 Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) & [Uvicorn](https://www.uvicorn.org/) (ASGI Server)
- **Deep Learning / NLP**: [PyTorch](https://pytorch.org/), [Hugging Face Transformers](https://huggingface.co/transformers/) (`SamLowe/roberta-base-go_emotions`, `microsoft/deberta-v3-base`)
- **Translation**: [deep-translator](https://github.com/nidhaloff/deep-translator)
- **Document Processing**: [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/)
- **OCR Engine**: [Pillow (`PIL`)](https://python-pillow.org/) & [PyTesseract](https://github.com/madmaze/pytesseract)

### Frontend
- **Option 1 (Standalone)**: Vanilla HTML5, Modern CSS (Glassmorphism & Responsive Flexbox/Grid), Vanilla JavaScript (Fetch API).
- **Option 2 (React SPA)**: React 19, Axios, Framer Motion, React Icons.

---

## 📁 Project Directory Structure

```text
sarcasm_detection/
├── app.py                     # Main FastAPI server and analysis orchestration pipeline
├── index.html                 # Standalone full-featured web dashboard (Glassmorphism UI)
├── requirements.txt           # Python dependencies
├── download_deberta.py        # Utility script to pre-cache DeBERTa-v3 weights
├── sarcasm_detector.py        # Sarcasm detection logic module
├── toxicity_model.py          # Toxicity classification module
├── language_detector.py       # Language detection utility
├── explainability.py          # Explainable AI placeholder
├── response_generator.py      # Automated response generator placeholder
├── models/
│   ├── deberta_engine.py      # Transformer-based emotion inference engine
│   ├── fusion_engine.py       # Heuristic & Transformer decision fusion
│   ├── rule_engine.py         # Heuristic rule definitions
│   └── microsoft_deberta/     # Local storage directory for downloaded transformer weights
├── utils/
│   ├── language.py            # Multilingual processing utilities
│   ├── ocr_reader.py          # Image OCR extraction wrapper
│   ├── pdf_reader.py          # PyMuPDF document extraction wrapper
│   ├── profanity.py           # Content moderation and profanity filters
│   └── summary.py             # Smart summarizer helper
├── frontend/                  # React Single-Page Application (CRA)
│   ├── package.json           # Frontend dependencies & build scripts
│   ├── public/                # Public assets & HTML template
│   └── src/
│       ├── App.js             # React application component
│       ├── App.css            # Component styles
│       ├── index.js           # React DOM root
│       └── index.css          # Global styling
└── uploads/                   # Temporary directory for file uploads
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python**: Version `3.9` or higher installed.
- **Node.js**: Version `18.x` or higher (if running the React frontend).
- **Tesseract OCR**:
  - **Windows**: Download and install the binary installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add it to your system `PATH`.
  - **Linux (Ubuntu/Debian)**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`

---

### 2. Clone & Environment Setup

Open your terminal or PowerShell in the project directory:

```bash
# Navigate to the project root
cd "c:/College_Files/Major Project/sarcasm_detection"

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

---

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install deep-translator
```

---

### 4. Model Download (Optional)

To pre-cache transformer models locally for offline performance:

```bash
python download_deberta.py
```

---

## ⚡ Running the Application

### Running the Backend API

Start the FastAPI ASGI server with auto-reload:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Alternative ReDoc UI**: `http://127.0.0.1:8000/redoc`

---

### Using the Standalone Web Dashboard

The repository includes a ready-to-use dark glassmorphism web interface ([`index.html`](index.html)):

1. Make sure your FastAPI backend is running on `http://127.0.0.1:8000`.
2. Simply double-click `index.html` or open it with your favorite browser:
   ```bash
   start index.html       # On Windows
   open index.html        # On macOS
   xdg-open index.html    # On Linux
   ```
3. Type text, upload images (OCR), or submit `.pdf` files for instant real-time analysis!

---

### Running the React Frontend

If you wish to use the dedicated React 19 Single Page App:

```bash
# Navigate to the frontend folder
cd frontend

# Install npm dependencies
npm install

# Start the React development server
npm start
```

The app will launch at `http://localhost:3000`.

---

## 📡 API Reference

### Endpoint: `POST /analyze`

Analyzes raw text, uploaded documents (`.pdf`), or uploaded images (`.png`, `.jpg`, `.jpeg`).

- **Content-Type**: `multipart/form-data`
- **Parameters**:
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `text` | `string (Form)` | Optional | The input text message or conversation snippet. |
  | `file` | `UploadFile (File)` | Optional | A `.pdf` document or image file (`.png`, `.jpg`, `.jpeg`). |

#### Sample `curl` Request

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "text=Wow great job on destroying the production database!"
```

---

### Sample Response

```json
{
  "clean_text": "Wow great job on destroying the production database!",
  "language": "English",
  "translation": "Wow great job on destroying the production database!",
  "sarcasm": "Sarcastic",
  "relationship": "Unknown",
  "rule_based_emotion": "Neutral",
  "deberta_emotion": {
    "emotion": "admiration",
    "confidence": 78.45
  },
  "hybrid_emotion": "admiration",
  "illegal_activity": false,
  "risk_level": "MEDIUM",
  "summary": "Wow great job on destroying the production database!",
  "confidence": 92.0,
  "model": "SentinelMind AI v2.0 (Hybrid NLP + Microsoft DeBERTa)"
}
```


#### Output Fields Description:
- `clean_text`: Sanitized input text with extreme profanities automatically redacted.
- `language`: Detected language (e.g., `English`, `Kannada`, `Tamil`, `Hindi`, `Kannada + English`, etc.).
- `translation`: English translated equivalent if input is non-English.
- `sarcasm`: `Sarcastic` or `Not Sarcastic`.
- `relationship`: Detected social dynamic (`Parent / Child`, `Friends`, `Teacher / Student`, `Close Relationship`, `Unknown`).
- `rule_based_emotion`: Emotion detected via rule heuristics (`Angry`, `Positive`, `Neutral`).
- `deberta_emotion`: Emotion and confidence predicted by the Transformer classification pipeline.
- `hybrid_emotion`: Final synthesized emotion label after running through the fusion engine.
- `illegal_activity`: Boolean flag (`true`/`false`) marking severe danger, threats, or weapons.
- `risk_level`: Evaluated severity rating (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- `confidence`: Overall confidence metric percentage.
- `summary`: Short extractive summary for long inputs.

---

## 🚦 Risk Level Matrix

| Risk Level | Trigger Condition | Example Scenario |
| :---: | :--- | :--- |
| <span style="color:red">**CRITICAL**</span> | `illegal_activity == true` | Threats of violence, weapon possession, terror keywords |
| <span style="color:orange">**HIGH**</span> | High-intensity negative emotions | Expressions of intense anger, rage, or fear |
| <span style="color:yellow">**MEDIUM**</span> | `sarcasm == "Sarcastic"` | Ambiguous sarcasm masking negative sentiment |
| <span style="color:green">**LOW**</span> | Standard conversational messages | Safe positive or neutral messages |

---

## 🔮 Contributing & Roadmap

- [x] Multilingual Kannada, Tamil, Hindi & code-mixed parsing
- [x] Multimodal image OCR & PDF document ingestion
- [x] Hybrid Rule + Transformer decision fusion
- [ ] Explainability visualizer using SHAP / LIME attention maps (`explainability.py`)
- [ ] Automated safe intervention response generator (`response_generator.py`)
- [ ] Speech-to-text audio ingestion module

Contributions, issues, and feature requests are welcome!

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute for academic and commercial projects.