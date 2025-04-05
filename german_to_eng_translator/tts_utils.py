import io
import logging
import time

import streamlit as st
import torch

TTS_ENGINE = "huggingface" 
HF_TTS_MODEL_NAME = "facebook/mms-tts-deu"
TORCH_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

hf_libraries_installed = False
gtts_installed = False
hf_processor = None
hf_model = None

try:
    import soundfile as sf
    from transformers import AutoProcessor, AutoModelForTextToWaveform

    hf_libraries_installed = True
except ImportError:
    if TTS_ENGINE == "huggingface":
        logging.warning("Required libraries for Hugging Face TTS (transformers, torch, soundfile) are not installed.")

try:
    from gtts import gTTS

    gtts_installed = True
except ImportError:
    if TTS_ENGINE == "gtts":
        logging.warning("Required library gTTS is not installed.")


@st.cache_resource
def load_hf_tts_model_and_processor(model_name: str) -> tuple[object | None, object | None]:
    """
    Load the Hugging Face TTS processor and model.

    Args:
        model_name (str): The name of the Hugging Face model.

    Returns:
        tuple: (processor, model) if successful; otherwise, (None, None).
    """
    if not hf_libraries_installed:
        logging.error("Cannot load HF model: Required libraries not installed.")
        return None, None

    try:
        logging.info("Loading HF TTS processor: %s", model_name)
        processor = AutoProcessor.from_pretrained(model_name)
        logging.info("Loading HF TTS model: %s on %s", model_name, TORCH_DEVICE)
        model = AutoModelForTextToWaveform.from_pretrained(model_name).to(TORCH_DEVICE)
        logging.info("HF TTS model and processor loaded successfully.")
        return processor, model
    except Exception as e:
        logging.error("Failed to load HF model/processor '%s': %s", model_name, e, exc_info=True)
        st.error(f"Error loading TTS model '{model_name}'. Check logs.", icon="🚨")
        return None, None


if TTS_ENGINE == "huggingface" and hf_libraries_installed:
    processor, model = load_hf_tts_model_and_processor(HF_TTS_MODEL_NAME)
    if processor and model:
        hf_processor, hf_model = processor, model
    else:
        logging.error("Failed to load Hugging Face model: %s", HF_TTS_MODEL_NAME)


def _generate_speech_audio_hf(text: str) -> tuple[bytes | None, str | None, str | None]:
    """
    Generate audio using the Hugging Face TTS engine.

    Args:
        text (str): Text to be converted to speech.

    Returns:
        tuple: (audio_bytes, audio_format, engine_name) if successful; otherwise, (None, None, None).
    """
    if not (hf_libraries_installed and hf_processor and hf_model) or not text:
        return None, None, None

    logging.info("HF TTS: Processing text: '%s...'", text[:30])
    start_time = time.time()
    try:
        inputs = hf_processor(text=text, return_tensors="pt").to(TORCH_DEVICE)
        with torch.no_grad():
            output = hf_model(**inputs)
            if hasattr(output, "waveform"):
                waveform = output.waveform
            elif hasattr(output, "audio"):
                waveform = output.audio
            else:
                waveform = next(iter(output.values()))
            waveform_cpu = waveform.cpu().numpy().squeeze()

        sampling_rate = hf_model.config.sampling_rate
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, waveform_cpu, sampling_rate, format="WAV")
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        elapsed = time.time() - start_time
        logging.info("HF TTS: Success %d bytes in %.2f sec.", len(audio_bytes), elapsed)
        return audio_bytes, "audio/wav", "Hugging Face"
    except Exception as e:
        logging.error("HF TTS failed for text '%s...': %s", text[:30], e, exc_info=True)
        return None, None, None


def _generate_speech_audio_gtts(text: str, lang: str = "de") -> tuple[bytes | None, str | None, str | None]:
    """
    Generate audio using the gTTS engine.

    Args:
        text (str): Text to be converted to speech.
        lang (str): Language code for the speech synthesis (default: "de").

    Returns:
        tuple: (audio_bytes, audio_format, engine_name) if successful; otherwise, (None, None, None).
    """
    if not (gtts_installed and text):
        return None, None, None

    logging.info("gTTS: Processing text: '%s...'", text[:30])
    start_time = time.time()
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_bytes = audio_fp.read()
        elapsed = time.time() - start_time
        logging.info("gTTS: Success %d bytes in %.2f sec.", len(audio_bytes), elapsed)
        return audio_bytes, "audio/mp3", "gTTS"
    except Exception as e:
        logging.error("gTTS failed for text '%s...': %s", text[:30], e, exc_info=True)
        return None, None, None


def generate_speech_audio(text: str, lang: str = "de") -> tuple[bytes | None, str | None, str | None]:
    """
    Generate speech audio bytes using the configured TTS engine.

    Args:
        text (str): The text to convert to speech.
        lang (str): The language code for speech synthesis (default: "de").

    Returns:
        tuple: (audio_bytes, audio_format, engine_name) if successful; otherwise, (None, None, None).
    """
    audio_bytes, audio_format, engine_name = None, None, None

    if TTS_ENGINE == "huggingface" and hf_libraries_installed and hf_processor and hf_model:
        audio_bytes, audio_format, engine_name = _generate_speech_audio_hf(text)
    elif TTS_ENGINE == "gtts" and gtts_installed:
        audio_bytes, audio_format, engine_name = _generate_speech_audio_gtts(text, lang)

    if audio_bytes is None and gtts_installed:
        if TTS_ENGINE != "gtts":
            logging.warning("Primary TTS failed or unavailable. Falling back to gTTS.")
        audio_bytes, audio_format, engine_name = _generate_speech_audio_gtts(text, lang)
        if engine_name:
            engine_name += " (Fallback)"

    if audio_bytes:
        logging.info("Generated audio using %s.", engine_name)
    else:
        logging.error("No TTS engine could generate audio.")

    return audio_bytes, audio_format, engine_name


def is_tts_available() -> bool:
    """
    Check if any TTS engine is configured and ready.

    Returns:
        bool: True if TTS is available, otherwise False.
    """
    if TTS_ENGINE == "huggingface":
        return hf_libraries_installed and hf_processor and hf_model
    if TTS_ENGINE == "gtts":
        return gtts_installed
    return gtts_installed


def get_tts_status() -> str:
    """
    Get a user-friendly status message about the TTS engine.

    Returns:
        str: The status message.
    """
    if TTS_ENGINE == "huggingface":
        if hf_libraries_installed and hf_processor and hf_model:
            return f"Using Hugging Face TTS model: `{HF_TTS_MODEL_NAME}` on `{TORCH_DEVICE}`."
        if hf_libraries_installed:
            return f"⚠️ Hugging Face libraries installed, but model `{HF_TTS_MODEL_NAME}` failed to load. Check logs. Trying fallbacks..."
        return "⚠️ Hugging Face TTS selected but required libraries (transformers, torch, soundfile) are not installed. Trying fallbacks..."
    if TTS_ENGINE == "gtts":
        return "Using gTTS for pronunciation." if gtts_installed else "⚠️ gTTS selected but not installed (pip install gTTS). TTS disabled."
    return "🔇 TTS is unavailable. Please install required libraries (gTTS or transformers, torch, soundfile)."
