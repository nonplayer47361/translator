# This file defines any custom types or interfaces used in the project, such as data structures for representing Braille characters or translation results.

from typing import Dict, List, Union

# Define a type for Braille character representation
BrailleCharacter = List[int]

# Define a type for the mapping of characters to Braille
BrailleMapping = Dict[str, Union[BrailleCharacter, List[BrailleCharacter]]]

# Define a type for translation results
class TranslationResult:
    def __init__(self, original_text: str, translated_braille: str):
        self.original_text = original_text
        self.translated_braille = translated_braille

    def __repr__(self):
        return f"TranslationResult(original_text={self.original_text}, translated_braille={self.translated_braille})"