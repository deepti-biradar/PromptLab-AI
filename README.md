# 🧪 PromptLab AI

PromptLab is a Streamlit-based AI prompt engineering laboratory powered by Google Gemini.

## Features

- 7 prompt engineering techniques:
  - Zero-shot
  - Few-shot
  - Chain-of-Thought / reasoning-oriented prompting
  - Role
  - Instruction
  - Contextual
  - Structured
- Gemini model selection
- Temperature and maximum-token controls
- Prompt preview
- PDF and TXT answer export
- Complete chat-history export
- Session-based conversation history
- English, Kannada and Hindi response options

## 1. Install Python

Use Python 3.10+.

## 2. Create a virtual environment (recommended)

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Add your Gemini API key

Copy `.streamlit/secrets.toml.example` to:

```text
.streamlit/secrets.toml
```

Then replace `YOUR_GEMINI_API_KEY` with your actual key.

For Streamlit Cloud, add the same value under the app's Secrets settings instead of committing `secrets.toml`.

## 5. Run

```bash
streamlit run app.py
```

The browser should open the PromptLab application.

## Project structure

```text
PromptLab_AI_Project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## Important

Never upload your real API key to GitHub. Keep `.streamlit/secrets.toml` private.

## Troubleshooting

### API key error
Make sure the secret is named exactly:

```text
GEMINI_API_KEY
```

### Model error
If a model is unavailable for your API account, choose another model from the sidebar.

### Quota error
Check the quota/billing status of your Google AI API project.

