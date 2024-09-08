import re
from enum import StrEnum
from pprint import pprint

from deep_translator import GoogleTranslator


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

    def extract_blocks_with_structure(self, file_content):
        """Extracts blocks including the entire structure (text lines, tabs, empty lines)."""
        print(repr(file_content))

        # Adjusted regex to match label and keep content without leading newlines
        pattern = re.compile(r'(\w+::)\n([\s\S]+?)(?=\w+::|\Z)', re.MULTILINE)

        matches = pattern.findall(file_content)

        pprint(matches)  # Check the matches to ensure tabs and structure are preserved

        blocks = {}
        for label, content in matches:
            print(repr(content))  # Print the content to inspect the structure
            lines = content.splitlines(keepends=True)  # Keep original newlines and tabs
            blocks[label] = lines

        # pprint(blocks)
        return blocks

    def extract_text_for_translation(self, blocks):
        """Extracts only the text lines for translation, ignoring 'done', 'prompt'."""
        text_blocks = {}
        for label, lines in blocks.items():
            text_lines = []
            for line in lines:
                match = re.search(r'(text|line|para|cont)\s+"([^"]+)"', line)
                if match:
                    text_lines.append(match.group(2))
            text_blocks[label] = " ".join(text_lines)
        return text_blocks

    def reassemble_blocks_with_translated_text(self, translated_text_blocks, original_blocks):
        """Replaces the text lines with translated ones, keeping the rest of the structure."""
        reassembled_blocks = {}

        for label, original_lines in original_blocks.items():
            translated_text = translated_text_blocks[label].split()
            reassembled_lines = []
            idx = 0
            for line in original_lines:
                match = re.search(r'(text|line|para|cont)\s+"([^"]+)"', line)
                if match:
                    # Extract the original line's length and replace it with the translated text
                    original_text = match.group(2)
                    length = len(original_text.split())
                    new_text = " ".join(translated_text[idx:idx + length])
                    # Preserve leading whitespace (tabs) in the original line
                    leading_whitespace = line[:line.find(match.group(1))]
                    reassembled_lines.append(f'{leading_whitespace}{match.group(1)} "{new_text}"\n')
                    idx += length
                else:
                    # For lines that don't need translation, retain them as they are (including empty lines)
                    reassembled_lines.append(line)
            reassembled_blocks[label] = "".join(reassembled_lines)  # Join lines with their original newlines
        return reassembled_blocks


if __name__ == '__main__':

    # Load the asm file
    with open("test.asm", "r") as f:
        file_content = f.read()

    # Extract text blocks
    translator = PokemonTranslate("pokemon.asm", "da")
    blocks = translator.extract_blocks_with_structure(file_content)

    # Concatenate text from each block for translation
    combined_blocks = translator.extract_text_for_translation(blocks)

    # Translate the text
    translated_blocks = {label: translator.translate(text) for label, text in combined_blocks.items()}

    # Reformat the translated text back into the original format
    reformatted_blocks = translator.reassemble_blocks_with_translated_text(translated_blocks, blocks)

    # Write the translated text back to the asm file
    with open("test_da.asm", "w") as f:
        for label, content in reformatted_blocks.items():
            f.write(f'{label}\n{content}\n')