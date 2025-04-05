import logging
import re

import streamlit as st
import ollama

OLLAMA_MODEL_NAME = "llama3:8b"


def get_german_example_sentence_ollama(german_word: str) -> str | None:
    """
    Generate a simple German example sentence for a given word using the Ollama API.

    Args:
        german_word (str): The German word to include in the example sentence.

    Returns:
        Optional[str]: The generated German sentence if successful; otherwise, None.
    """
    if not german_word:
        return None

    prompt = (
        f"Erstelle EINEN einfachen deutschen Beispielsatz mit dem Wort '{german_word}'.\n"
        "WICHTIG: Der Satz MUSS auf DEUTSCH sein.\n"
        "Antworte NUR auf Deutsch.\n"
        "Der Satz sollte für Sprachlerner (A1/A2 Niveau) geeignet sein.\n"
        "Gib NUR den Satz selbst aus, ohne zusätzliche Erklärungen, Anführungszeichen oder Markdown.\n"
        "Beispiel für 'Buch': Das ist ein interessantes Buch.\n"
        "Beispiel für 'gehen': Wir gehen heute ins Kino.\n"
        "Beispiel für 'rot': Mein Lieblingsauto ist rot."
    )

    try:
        logging.info(
            "Sending GERMAN example request to Ollama model '%s' for word '%s'",
            OLLAMA_MODEL_NAME,
            german_word,
        )
        response = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein Assistent, der EINFACHE deutsche Beispielsätze für deutsche Wörter liefert. "
                        "Antworte IMMER NUR mit dem deutschen Satz selbst, sonst nichts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        sentence = response.get("message", {}).get("content", "").strip()

        if not sentence:
            logging.warning(
                "Ollama returned empty content for GERMAN word '%s'. Response: %s",
                german_word,
                response,
            )
            return None

        # Clean potential markdown, quotes, list markers, or unwanted prefixes.
        sentence = re.sub(r'^\s*["`\'\*>\-\s]+|["`\'\*]+\s*$', "", sentence).strip()
        sentence = re.sub(r"^(Beispiel|Example)\s*:\s*", "", sentence, flags=re.IGNORECASE).strip()

        if not re.search(r"\b" + re.escape(german_word) + r"\b", sentence, re.IGNORECASE):
            logging.warning(
                "Generated sentence for '%s' might not contain the exact word: '%s'",
                german_word,
                sentence,
            )

        common_english_words = {" the ", " is ", " are ", " was ", " were ", " a ", " an ", " he ", " she ", " it ", " you "}
        if any(eng_word in f" {sentence.lower()} " for eng_word in common_english_words):
            logging.warning(
                "Ollama response for '%s' appears to contain English words: '%s'",
                german_word,
                sentence,
            )

        return sentence

    except Exception as e:
        logging.error(
            "Ollama API call failed for model '%s': %s",
            OLLAMA_MODEL_NAME,
            e,
            exc_info=True,
        )
        st.error(
            f"Error generating example: Failed to connect to Ollama or model '{OLLAMA_MODEL_NAME}' not available.",
            icon="🚨",
        )
        return None
