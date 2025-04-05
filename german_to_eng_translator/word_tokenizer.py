import re
from typing import List


def tokenize_sentence(sentence: str) -> List[str]:
    """
    Split a sentence into words using basic punctuation handling.

    Args:
        sentence (str): The input sentence.

    Returns:
        List[str]: A list of words. Returns an empty list if the input is empty.
    """
    if not sentence:
        return []
    return re.findall(r'\b\w+\b', sentence)


def split_sentence_with_delimiters(sentence: str) -> List[str]:
    """
    Split a sentence into a list of words and delimiters, preserving the original structure.

    Args:
        sentence (str): The input sentence.

    Returns:
        List[str]: A list of strings, alternating between words and delimiters.
                   Returns an empty list if the input is empty.
    """
    if not sentence:
        return []
    parts = re.split(r'(\b\w+\b)', sentence)
    return [part for part in parts if part]


if __name__ == '__main__':
    test_sentence = "Das Wetter ist heute schön."
    print("Split with delimiters:", split_sentence_with_delimiters(test_sentence))
    test_sentence_punct = "Hallo! Wie geht's? Das ist gut."
    print("Split with delimiters:", split_sentence_with_delimiters(test_sentence_punct))
