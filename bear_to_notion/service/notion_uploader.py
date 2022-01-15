from notion.block import PageBlock, CollectionViewBlock
from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from bear_to_notion.model import Model
from bear_to_notion.model.markdown import Markdown

from md2notion.upload import upload

from pathlib import Path
import json
import sys

class NotionUploader(Model):

    def __init__(self, root, notion_token, disallowed_tags, dry_run):
        super(NotionUploader, self).__init__()

        self._client = NotionClient(token_v2=notion_token)
        self._root_page = self._client.get_block(root)
        assert isinstance(self._root_page, PageBlock)
        self._disallowed_tags = disallowed_tags
        self._dry_run = dry_run
        self._page_by_tag = {}
        self._collection_view_by_tag = {}

    def upload(self, markdown_files):
        filtered_markdown_files = self.__filter_markdown_files(markdown_files)
        self.__print(f"The number of all markdown files is {len(markdown_files)}.")
        self.__print(f"The number of filtered markdown files (to be uploaded to notion) is {len(filtered_markdown_files)}.")


        self.__create_tag_pages(filtered_markdown_files)

        for markdown in filtered_markdown_files:
            self.__upload_markdown(markdown)

    def __filter_markdown_files(self, markdown_files):
        return list(filter(self.__filter_markdown, markdown_files))

    def __filter_markdown(self, markdown: Markdown):
        for disallowed_tag in self._disallowed_tags:
            if disallowed_tag in markdown.tag:
                return False
        return True

    def __upload_markdown(self, markdown: Markdown):
        self.__print(f"Uploading {markdown.name}(tag: {markdown.tag}) to Notion.so")
        sys.stdout.flush()
        if self._dry_run:
            return

        def convert_image_path(image_path, md_file_path):
            return Path(md_file_path).parent / image_path
        with open(markdown.path, "r", encoding="utf-8") as md_file:
            #md_file.__dict__["name"] = markdown.path
            #upload(md_file, new_page, imagePathFunc=convert_image_path, notionPyRendererCls=addHtmlImgTagExtension(NotionPyRenderer))

            collection_view: CollectionViewBlock = self._collection_view_by_tag[markdown.tag]
            new_row: CollectionRowBlock = collection_view.collection.add_row(title=markdown.name)
            new_row.set_property("created_at", markdown.created_at)

            upload(md_file, new_row)

    def __create_tag_pages(self, markdown_files: [Markdown]):
        tag_dict = {}
        for markdown in markdown_files:
            current = tag_dict
            for tag in markdown.tag.split('/'):
                if tag not in current:
                    current[tag] = {}
                current = current[tag]

        if self._dry_run:
            self.__print(json.dumps(tag_dict, sort_keys=True, indent=2))
        else:
            self.__create_tag_pages_recursively(self._root_page, [], tag_dict)
        self.__print("Tag pages have been created.")

    def __create_tag_pages_recursively(self, current_page: PageBlock, current_tag_list: [str], current_tag_dict: dict[str]):
        for tag, child_dict in current_tag_dict.items():
            current_tag_list.append(tag)
            next_page: PageBlock = current_page.children.add_new(PageBlock, title=tag)
            self._page_by_tag['/'.join(current_tag_list)] = next_page
            self.__create_tag_pages_recursively(next_page, current_tag_list, current_tag_dict[tag])
            current_tag_list.pop()
        self._collection_view_by_tag['/'.join(current_tag_list)] = self.__create_list_collection(current_page)

    # Create database
    def __create_list_collection(self, parent_page: PageBlock):
        collection_view: CollectionViewBlock = parent_page.children.add_new(CollectionViewBlock)
        collection_view.collection = self._client.get_collection(
            self._client.create_record("collection", parent=collection_view, schema=self.__get_collection_schema())
        )
        collection_view.views.add_new(view_type="list")
        collection_view.title = "__notes"
        return collection_view

    def __get_collection_schema(self):
        return {
            "=d{|": {
                "name": "Tags",
                "type": "multi_select",
                "options": [],
            },
            "created_at": {"name": "Created at", "type": "date"},
            "title": {"name": "Name", "type": "title"},
        }

    def __print(self, text):
        print(f"[info] {'(dry-run)' if self._dry_run else ''} {text}")
