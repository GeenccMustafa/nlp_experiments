import logging
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def translate_text(
    text_to_translate: str, source_lang: str = "de", target_lang: str = "en"
) -> str | None:
    """
    Translate text using the MyMemory API.

    Args:
        text_to_translate (str): The text to translate.
        source_lang (str): The source language code (default: 'de').
        target_lang (str): The target language code (default: 'en').

    Returns:
        Optional[str]: The translated text if successful, otherwise None.
    """
    if not text_to_translate:
        return None

    api_url = "https://api.mymemory.translated.net/get"
    params = {"q": text_to_translate, "langpair": f"{source_lang}|{target_lang}"}

    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        translated_text = data.get("responseData", {}).get("translatedText")
        if translated_text:
            if "MYMEMORY WARNING" in translated_text:
                logging.warning("Translation response contained MyMemory DB warning.")
                translated_text = (
                    translated_text.split(" NMT")[0].split(" MT ")[0].strip()
                )
            return translated_text

        error_details = data.get("responseDetails", "No details provided.")
        logging.error("Could not extract translation. API Response Details: %s", error_details)
        return None

    except requests.exceptions.Timeout:
        logging.error("API request timed out for text: '%s'", text_to_translate)
    except requests.exceptions.RequestException as e:
        logging.error("API request failed: %s", e)
    except ValueError:
        logging.error("Failed to decode JSON response: %s", response.text)
    except Exception as e:
        logging.error("An unexpected error occurred during translation: %s", e)

    return None
