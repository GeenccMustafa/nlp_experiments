import sys
import re
import logging
from functools import partial

import streamlit as st

st.set_page_config(
    page_title="Interactive Translator + DE Examples + Local TTS",
    page_icon="🇩🇪🗣️",
    layout="wide"
)

try:
    from translation_api import translate_text
except ImportError:
    st.error("Missing `translation_api.py`.")
    st.stop()

try:
    from word_tokenizer import split_sentence_with_delimiters
except ImportError:
    st.error("Missing `word_tokenizer.py`.")
    st.stop()

try:
    from tts_utils import (
        generate_speech_audio,
        is_tts_available,
        get_tts_status,
        TTS_ENGINE,
        HF_TTS_MODEL_NAME,
    )
except ImportError:
    st.error("Missing `tts_utils.py`.")
    st.stop()

try:
    from ollama_utils import get_german_example_sentence_ollama, OLLAMA_MODEL_NAME
except ImportError:
    st.error("Missing `ollama_utils.py`.")
    st.stop()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if "input_sentence" not in st.session_state:
    st.session_state.input_sentence = ""
if "word_translation_result" not in st.session_state:
    st.session_state.word_translation_result = None
if "sentence_translation_result" not in st.session_state:
    st.session_state.sentence_translation_result = None
if "active_translation_word" not in st.session_state:
    st.session_state.active_translation_word = None
if "german_example_sentence_result" not in st.session_state:
    st.session_state.german_example_sentence_result = None
if "english_example_translation_result" not in st.session_state:
    st.session_state.english_example_translation_result = None
if "show_word_buttons" not in st.session_state:
    st.session_state.show_word_buttons = False
if "tts_audio_bytes" not in st.session_state:
    st.session_state.tts_audio_bytes = None
if "tts_audio_format" not in st.session_state:
    st.session_state.tts_audio_format = None


def handle_word_click(word: str) -> None:
    """
    Handles the logic when a user clicks on a word button:
    - Resets relevant session state variables
    - Translates the word
    - Generates a German example sentence
    - Translates the example sentence
    - Triggers a rerun of the Streamlit app

    Args:
        word (str): The clicked German word.
    """
    logging.info("Word button clicked for: '%s'", word)
    st.session_state.active_translation_word = word
    st.session_state.sentence_translation_result = None
    st.session_state.word_translation_result = None
    st.session_state.german_example_sentence_result = None
    st.session_state.english_example_translation_result = None
    st.session_state.tts_audio_bytes = None

    col_trans, col_example = st.columns(2)
    with col_trans, st.spinner(f"Translating '{word}'..."):
        english_translation = translate_text(word, source_lang="de", target_lang="en")
        st.session_state.word_translation_result = (
            word,
            english_translation if english_translation else "[Translation Failed]",
        )
        if not english_translation:
            logging.error("Failed to translate word '%s'.", word)
    with col_example, st.spinner(f"Generating example for '{word}'..."):
        german_example = get_german_example_sentence_ollama(word)
        st.session_state.german_example_sentence_result = german_example

    if st.session_state.german_example_sentence_result:
        german_example_to_translate = st.session_state.german_example_sentence_result
        logging.info("Translating example: '%s'", german_example_to_translate)
        with col_trans, st.spinner("Translating example..."):
            english_example_translation = translate_text(
                german_example_to_translate, source_lang="de", target_lang="en"
            )
            st.session_state.english_example_translation_result = (
                english_example_translation if english_example_translation else "[Example Translation Failed]"
            )
    else:
        logging.info("No German example sentence generated for '%s'.", word)
        st.session_state.english_example_translation_result = None

    st.rerun()


def handle_tts_click(text_to_speak: str, lang: str = "de") -> None:
    """
    Generates text-to-speech audio for the given input text.

    Args:
        text_to_speak (str): The text to convert to speech.
        lang (str): Language code for the TTS engine (default is 'de').
    """
    if not text_to_speak:
        return
    logging.info("TTS requested for: '%s...'", text_to_speak[:30])
    st.session_state.tts_audio_bytes = None
    st.session_state.tts_audio_format = None
    with st.spinner("Generating audio..."):
        audio_bytes, audio_format, engine_name = generate_speech_audio(text_to_speak, lang)
    if audio_bytes and audio_format:
        st.session_state.tts_audio_bytes = audio_bytes
        st.session_state.tts_audio_format = audio_format
        logging.info("Audio generated successfully by %s, format: %s", engine_name, audio_format)
        st.toast(f"Audio ready ({engine_name})", icon="🔊")
    else:
        logging.error("Failed to generate audio for '%s...'", text_to_speak[:30])
        st.toast("Failed to generate audio.", icon="🔇")
    st.rerun()


def update_input_state() -> None:
    """
    Callback function triggered when the user edits the input sentence.
    Resets all session state related to previous translations, examples, and TTS.
    """
    logging.info("Input text changed callback triggered.")
    if st.session_state.input_sentence != st.session_state.get("sentence_input_widget", ""):
        logging.info("Input text changed. Resetting states.")
        st.session_state.input_sentence = st.session_state.sentence_input_widget
        st.session_state.word_translation_result = None
        st.session_state.sentence_translation_result = None
        st.session_state.active_translation_word = None
        st.session_state.german_example_sentence_result = None
        st.session_state.english_example_translation_result = None
        st.session_state.show_word_buttons = False
        st.session_state.tts_audio_bytes = None


st.title("🇩🇪🗣️ Interactive Translator + Examples + Local TTS")
st.markdown("Enter a German sentence, click 'Show Words', then click a word for details and pronunciation.")

tts_status_message = get_tts_status()
if "⚠️" in tts_status_message or "🔇" in tts_status_message:
    st.warning(tts_status_message)
else:
    st.info(tts_status_message)

tts_globally_available = is_tts_available()

st.text_area(
    "Enter German Sentence:",
    key="sentence_input_widget",
    value=st.session_state.input_sentence,
    height=100,
    on_change=update_input_state,
    placeholder="z.B. Angela Merkel besuchte Berlin letzte Woche.",
)
current_sentence = st.session_state.input_sentence

if current_sentence:
    col_actions1, col_actions2 = st.columns([0.7, 0.3])
    with col_actions1:
        button_label = "Hide Words" if st.session_state.show_word_buttons else "Show Words to Click"
        if st.button(button_label, key="toggle_words_btn", type="secondary", use_container_width=True):
            st.session_state.show_word_buttons = not st.session_state.show_word_buttons
            if not st.session_state.show_word_buttons:
                st.session_state.active_translation_word = None
                st.session_state.word_translation_result = None
                st.session_state.german_example_sentence_result = None
                st.session_state.english_example_translation_result = None
                st.session_state.tts_audio_bytes = None
            st.rerun()
    with col_actions2:
        if tts_globally_available:
            st.button(
                "🗣️ Hear Original",
                key="tts_original_sentence",
                on_click=handle_tts_click,
                args=(current_sentence, "de"),
                help="Hear the original German sentence",
                use_container_width=True,
                disabled=not current_sentence,
            )

if st.session_state.show_word_buttons and current_sentence:
    st.divider()
    st.markdown("#### Click a Word Below:")
    with st.container():
        parts = split_sentence_with_delimiters(current_sentence)
        words_with_original_case = [part for part in parts if re.search(r"\w", part)]
        unique_words_tracker = {}
        display_words_list = []
        for word in words_with_original_case:
            lower_word = word.lower()
            if lower_word not in unique_words_tracker:
                unique_words_tracker[lower_word] = word
                display_words_list.append(word)

        if not display_words_list:
            st.warning("No words found in the sentence.")
        else:
            MAX_COLS_PER_ROW = 6
            num_words = len(display_words_list)
            num_rows = -(-num_words // MAX_COLS_PER_ROW)
            word_idx = 0
            for _ in range(num_rows):
                cols = st.columns(MAX_COLS_PER_ROW)
                for col in cols:
                    if word_idx < num_words:
                        word_to_display = display_words_list[word_idx]
                        button_key = f"word_{word_idx}_{word_to_display.lower()}"
                        on_click_callback = partial(handle_word_click, word_to_display)
                        button_type = "primary" if st.session_state.active_translation_word == word_to_display else "secondary"
                        col.button(
                            label=word_to_display,
                            key=button_key,
                            on_click=on_click_callback,
                            type=button_type,
                            use_container_width=True,
                        )
                        word_idx += 1
    st.divider()

st.subheader("Translation, Example & Pronunciation")
audio_placeholder = st.empty()
if st.session_state.get("tts_audio_bytes") and st.session_state.get("tts_audio_format"):
    audio_placeholder.audio(
        st.session_state.tts_audio_bytes, format=st.session_state.tts_audio_format
    )

result_placeholder = st.container()
with result_placeholder:
    if st.session_state.active_translation_word:
        original_german_word = st.session_state.active_translation_word
        translation_data = st.session_state.word_translation_result
        german_example_sentence = st.session_state.german_example_sentence_result
        english_example_translation = st.session_state.english_example_translation_result

        if translation_data and translation_data[0] == original_german_word:
            _, english_translation = translation_data
            col_word_text, col_word_tts = st.columns([0.9, 0.1])
            with col_word_text:
                if english_translation and "[Translation Failed]" not in english_translation:
                    st.markdown(f"**{original_german_word}** (DE) ➔ **{english_translation}** (EN)")
                else:
                    st.error(f"Could not translate '{original_german_word}'.")
            with col_word_tts:
                if tts_globally_available:
                    tts_button_key_word = f"tts_word_{original_german_word.lower()}"
                    st.button(
                        "🗣️",
                        key=tts_button_key_word,
                        on_click=handle_tts_click,
                        args=(original_german_word,),
                        help=f"Hear '{original_german_word}'",
                    )
                else:
                    st.caption("TTS N/A")
            st.divider()
            if german_example_sentence:
                col_ex_text, col_ex_tts = st.columns([0.9, 0.1])
                with col_ex_text:
                    st.markdown("**Deutsches Beispiel:**")
                    st.info(german_example_sentence)
                    if english_example_translation:
                        st.markdown("**(Translation:)**")
                        st.markdown(f"*{english_example_translation}*")
                    elif st.session_state.word_translation_result:
                        st.caption("*(Example translation pending/failed...)*")
                with col_ex_tts:
                    if tts_globally_available:
                        tts_button_key_example = f"tts_example_{hash(german_example_sentence)}"
                        st.button(
                            "🗣️",
                            key=tts_button_key_example,
                            on_click=handle_tts_click,
                            args=(german_example_sentence,),
                            help="Hear example sentence",
                        )
                    else:
                        st.caption("TTS N/A")
            elif st.session_state.word_translation_result is not None:
                st.warning(f"Could not generate German example for '{original_german_word}'.", icon="⚠️")
        elif not translation_data and st.session_state.active_translation_word:
            st.info(f"Processing '{original_german_word}'...")
    elif st.session_state.sentence_translation_result:
        translation = st.session_state.sentence_translation_result
        if translation and "[Failed]" not in translation:
            col_trans_text, col_trans_tts = st.columns([0.9, 0.1])
            with col_trans_text:
                st.markdown("**Full Sentence Translation (EN):**")
                st.markdown(translation)
            with col_trans_tts:
                if tts_globally_available:
                    tts_button_key_full = f"tts_full_sentence_{hash(translation)}"
                    st.button(
                        "🗣️",
                        key=tts_button_key_full,
                        on_click=handle_tts_click,
                        args=(translation, "en"),
                        help="Hear full sentence translation",
                    )
                else:
                    st.caption("TTS N/A")
        elif translation:
            st.error("Could not translate the full sentence.")
    else:
        st.info("Enter a sentence and click 'Show Words', or click 'Translate Full Sentence'.")

if st.button("Translate Full Sentence", disabled=not current_sentence, key="full_translate_btn", type="primary"):
    logging.info("Translating full sentence: '%s...'", current_sentence[:50])
    st.session_state.active_translation_word = None
    st.session_state.word_translation_result = None
    st.session_state.german_example_sentence_result = None
    st.session_state.english_example_translation_result = None
    st.session_state.tts_audio_bytes = None

    with st.spinner("Translating full sentence..."):
        full_translation = translate_text(current_sentence, source_lang="de", target_lang="en")
        st.session_state.sentence_translation_result = (
            full_translation if full_translation else "[Full Translation Failed]"
        )
    if not full_translation:
        logging.error("Failed to translate the full sentence.")
    st.rerun()

st.divider()
st.caption(
    f"Translation: MyMemory API | Examples: Ollama ({OLLAMA_MODEL_NAME}) | "
    f"Pronunciation: {TTS_ENGINE} ({'Available' if tts_globally_available else 'Unavailable'})"
)
