# AI Mystery Detective Team: The Vanishing Aurora Diamond

A beginner-friendly multi-agent mystery investigation system using Python, Gradio, and Google GenAI SDK.

## Overview
This system implements a single Lead Investigator perspective across 5 specialized AI agent roles:
1. **Detective**: Reconstructs timelines and confirmed facts.
2. **Evidence**: Evaluates clues A-G for proof vs inference.
3. **Suspect**: Compares all 4 suspects across standardized criteria.
4. **Skeptic**: Challenges assumptions and card access identity fallacies.
5. **Chief**: Delivers accountable verdict, confidence rating, and next actions.

Supports running with Evidence E (Blue Velvet Fibers) removed to compare verdict shifts and confidence changes.

## Setup Instructions

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure API Key**:
Create `.env` file or export your Gemini API Key:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

3. **Run Application**:
```bash
python app.py
```
Open http://127.0.0.1:7860 in your browser.
