from pathlib import Path
from notion.block import CodeBlock
from md2notion.upload import convert
from dateutil.parser import parse
import re
import json

from bear_to_notion.model.markdown import Markdown

BEAR_TAG_PATTERN = r'(\s|\n|^)#([a-z][a-z\-\/ ]*[a-z])(#|\n|$)'


class Bear:

    def __init__(self, bearbk_path):
        self._markdown_files = []

        self.__load(bearbk_path)

    @property
    def markdown_files(self):
        return self._markdown_files

    def __load(self, bearbk_path):
        for textbundle_path in Path(bearbk_path).iterdir():
            if textbundle_path.suffix != ".textbundle":
                continue
            name = self.__get_name(textbundle_path)
            tag = self.__find_tag(textbundle_path)
            created_at = self.__created_at(textbundle_path)
            modified_at = self.__modified_at(textbundle_path)
            if tag is None:
                print("[info] failed to find tag from: " + name)
            self._markdown_files.append(Markdown(name, tag, textbundle_path / "text.txt", created_at, modified_at))

    def __get_name(self, textbundle_path):
        return textbundle_path.stem

    def __find_tag(self, textbundle_path):
        def find_tag_in_block_descriptor(block_descriptor):
            tag = None
            if block_descriptor['type'] is not CodeBlock and 'title' in block_descriptor:
                result = re.findall(BEAR_TAG_PATTERN, block_descriptor['title'])
                if len(result) != 0 and len(result[0]) > 1:
                    tag = result[0][1]
            if 'children' not in block_descriptor:
                return tag
            for child in block_descriptor['children']:
                candidate = find_tag_in_block_descriptor(child)
                if candidate is not None and (tag is None or len(candidate) > len(tag)):
                    tag = candidate
            return tag

        with open(textbundle_path / "text.txt", "r", encoding="utf-8") as md_file:
            rendered = convert(md_file)
            tag = None
            for idx, block_descriptor in enumerate(rendered):
                candidate = find_tag_in_block_descriptor(block_descriptor)
                if candidate is not None and (tag is None or len(candidate) > len(tag)):
                    tag = candidate
            return tag

    def __created_at(self, textbundle_path):
        with open(textbundle_path / "info.json", "r") as info_json:
            info = json.load(info_json)
            return parse(info['net.shinyfrog.bear']['creationDate'])

    def __modified_at(self, textbundle_path):
        with open(textbundle_path / "info.json", "r") as info_json:
            info = json.load(info_json)
            return parse(info['net.shinyfrog.bear']['modificationDate'])