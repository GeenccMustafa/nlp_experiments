# ner_utils.py

import logging

import spacy
import streamlit as st

# --- Configuration ---
NER_COLORS = {
    "PER": "#FFADAD",   # Person
    "LOC": "#ADD8E6",   # Location
    "ORG": "#90EE90",   # Organization
    "MISC": "#FFD6A5",  # Miscellaneous
    "DEFAULT": "#FFFFFF",  # Default (non-entities)
}

SPACY_MODEL_NAME = "de_core_news_sm"


@st.cache_resource
def load_spacy_model(model_name: str = SPACY_MODEL_NAME):
    """
    Loads and caches the specified spaCy language model using Streamlit.

    Args:
        model_name (str): Name of the spaCy model to load.

    Returns:
        spacy.Language: Loaded spaCy language model instance.
    """
    try:
        logging.info(f"Loading spaCy model: {model_name}")
        return spacy.load(model_name)
    except OSError:
        message = (
            f"spaCy model '{model_name}' not found. "
            f"Run: `python -m spacy download {model_name}`"
        )
        logging.error(message)
        st.error(message, icon="🚨")
    except Exception as e:
        logging.exception(f"Unexpected error loading spaCy model: {e}")
        st.error(
            f"An error occurred while loading the spaCy model '{model_name}'.", icon="🚨"
        )
    return None


nlp = load_spacy_model()


def get_entities(sentence: str) -> dict[str, str]:
    """
    Extracts named entities from a sentence and maps each token to its NER label.

    Args:
        sentence (str): The input sentence to analyze.

    Returns:
        dict[str, str]: Dictionary of token (lowercase) to NER tag.
    """
    if not nlp or not sentence:
        return {}

    try:
        doc = nlp(sentence)
        entities = {
            token.text.lower(): ent.label_
            for ent in doc.ents
            for token in ent
        }
        logging.info(f"Entities found: {entities}")
        return entities
    except Exception as e:
        logging.exception(f"NER processing failed for input: {sentence[:30]}...: {e}")
        return {}


def get_ner_legend_html() -> str:
    """
    Generates the HTML string for a legend showing NER tag colors.

    Returns:
        str: HTML representation of the NER legend.
    """
    if not NER_COLORS:
        return ""

    legend_html = ""
    for tag in sorted(tag for tag in NER_COLORS if tag != "DEFAULT"):
        color = NER_COLORS[tag]
        legend_html += (
            f'<span style="background-color:{color}; padding: 3px 6px; '
            f'margin: 2px; border-radius: 4px; display: inline-block; '
            f'font-size: 0.9em;">{tag}</span> '
        )

    return f'<div style="margin-bottom: 10px;"><b>NER Legend:</b> {legend_html}</div>'
