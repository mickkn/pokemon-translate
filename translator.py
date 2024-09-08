from enum import StrEnum
import deepl
import googletrans
import os
from deep_translator import GoogleTranslator
import re

class Language(StrEnum):

    DANISH = "da"


class PokemonTranslate(object):

    def __init__(self, file_path: str, lang: str):
        self.file_path = file_path
        self.lang = lang
        self.translator = GoogleTranslator(source='auto', target=self.lang)

    def translate(self, text: str) -> str:
        """Translate the text to the given language

        Args:
            text: The text to translate.

        """
        return self.translator.translate(text)

    def extract_text_blocks(self, file_content: str) -> dict:
        """Extracts and groups text blocks from the asm file."""
        pattern = re.compile(r'(\w+::)\s*([\s\S]+?)(?=\w+::|\Z)', re.MULTILINE)
        matches = pattern.findall(file_content)

        blocks = {}
        for label, content in matches:
            lines = re.findall(r'(text|line|para|cont)\s+"([^"]+)"', content)
            blocks[label] = lines
        return blocks

    def concatenate_text(self, blocks):
        """Concatenate text from each block for translation."""
        combined_blocks = {}
        for label, lines in blocks.items():
            full_text = " ".join([text for _, text in lines])
            combined_blocks[label] = full_text
        return combined_blocks

    def reformat_translated_blocks(self, translated_blocks, original_blocks):
        """Reformats the translated text back into the original format."""
        reformatted_blocks = {}
        for label, translated_text in translated_blocks.items():
            original_lines = original_blocks[label]
            # Break translated_text into chunks based on original line count
            translated_lines = translated_text.split()  # Adjust splitting logic as needed
            reformatted_content = []
            idx = 0
            for original_line in original_lines:
                keyword, _ = original_line
                length = len(_)
                reformatted_content.append(f'{keyword} "{translated_lines[idx:idx + length]}"')
                idx += length
            reformatted_blocks[label] = "\n".join(reformatted_content)
        return reformatted_blocks



if __name__ == '__main__':

    # Load the asm file
    with open("test.asm", "r") as f:
        file_content = f.read()

    # Extract text blocks
    translator = PokemonTranslate("pokemon.asm", "da")
    blocks = translator.extract_text_blocks(file_content)

    # Concatenate text from each block for translation
    combined_blocks = translator.concatenate_text(blocks)

    # Translate the text
    translated_blocks = {label: translator.translate(text) for label, text in combined_blocks.items()}

    # Reformat the translated text back into the original format
    reformatted_blocks = translator.reformat_translated_blocks(translated_blocks, blocks)

    # Write the translated text back to the asm file
    with open("test_da.asm", "w") as f:
        for label, content in reformatted_blocks.items():
            f.write(f'{label}\n{content}\n')