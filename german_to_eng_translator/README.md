# 🇩🇪 Interactive German Sentence Translator + Example Generator + TTS

🎥 **[Watch Demo on YouTube](https://www.youtube.com/watch?v=XqK_CJWDzUE)**

A Streamlit-based web application that enables users to:

1. 🔍 Enter a German sentence and see it tokenized into clickable words.
2. 🧠 Click on a word to get:

    2.1. Its English translation (via MyMemory API).
    2.2. A simple German example sentence using that word (generated with Ollama).
    2.3. The English translation of that example sentence.

3. 🔈 Play audio for:

    3.1. The original German sentence
    3.2. The selected word
    3.3. The generated example sentence (via HuggingFace TTS or gTTS)

## ✅ Features

- Modular codebase (translation_api.py, ollama_utils.py, tts_utils.py, word_tokenizer.py, app.py)
- Uses MyMemory API for translations
- Uses Ollama for generating simple example sentences
- Supports both HuggingFace and gTTS for text-to-speech (TTS)
- Interactive, fast, and fully local (except APIs)
- Professional logging and error handling

## 🗂️ Project Structure
```
.
├── app.py                        # Main Streamlit app
├── ollama_utils.py               # Generates example sentences via Ollama
├── tts_utils.py                  # Text-to-Speech handling via HuggingFace or gTTS
├── translation_api.py            # Uses MyMemory API to translate text
├── word_tokenizer.py             # Splits input into words and delimiters
├── environment.yaml              # Conda environment with dependencies
├── README.md                     # This file
```

## 🚀 How to Run the App

1. Create and Activate Environment

```
conda env create -f environment.yaml
conda activate my_streamlit_app
```

2. Run the Streamlit App

```
python -m streamlit run app.py
```

## 📦 Dependencies
Defined in environment.yaml, including:

```
streamlit
transformers
torch
gtts
soundfile
requests
Ollama 
```
## 🌐 APIs and Models Used
```
| Component               | Source / Library                                    |
|------------------------|-----------------------------------------------------|
| Translation            | [MyMemory Translated API](https://mymemory.translated.net/doc/spec.php) |
| Example Sentence Gen.  | [Ollama](https://ollama.com/) (e.g., `llama3:8b`)    |
| Text-to-Speech (TTS)   | HuggingFace MMS or [Google gTTS](https://pypi.org/project/gTTS/) |
```

## ✨ Example Use Case
```
Angela Merkel besuchte Berlin letzte Woche.
```

Get:
- Word-by-word translations
- Example sentence for a clicked word like “besuchte” → „Er besuchte seine Großeltern am Wochenende.“
- TTS playback of original and example sentences

## 📌 Notes

- Requires an Ollama model like llama3:8b to be available locally or via API
- Internet connection needed for MyMemory and gTTS
- HuggingFace TTS requires transformers, torch, and soundfile
