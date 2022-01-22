from notion.block import PageBlock, CollectionViewBlock
from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from bear_to_notion.model import Model
from bear_to_notion.model.markdown import Markdown

from md2notion.upload import upload

from pathlib import Path
import sys

class NotionUploader(Model):

    def __init__(self, root, notion_token, disallowed_tags, dry_run):
        super(NotionUploader, self).__init__()

        self._client = NotionClient(token_v2=notion_token)
        self._root_page = self._client.get_block(root)
        assert isinstance(self._root_page, PageBlock)
        self._disallowed_tags = disallowed_tags
        self._dry_run = dry_run

    def upload(self, markdown_files):
        filtered_markdown_files = self.__filter_markdown_files(markdown_files)
        self.__print(f"The number of all markdown files is {len(markdown_files)}.")
        self.__print(f"The number of filtered markdown files (to be uploaded to notion) is {len(filtered_markdown_files)}.")

        collection_view = self.__create_list_collection(self._root_page)

        for markdown in filtered_markdown_files:
            self.__upload_markdown(markdown, collection_view)

    def __filter_markdown_files(self, markdown_files):
        return list(filter(self.__filter_markdown, markdown_files))

    def __filter_markdown(self, markdown: Markdown):
        for disallowed_tag in self._disallowed_tags:
            if disallowed_tag in markdown.tag:
                return False
        return True

    def __upload_markdown(self, markdown: Markdown, collection_view: CollectionViewBlock):
        self.__print(f"Uploading {markdown.name}(tag: {markdown.tag}) to Notion.so")
        sys.stdout.flush()
        if self._dry_run:
            return

        def convert_image_path(image_path, md_file_path):
            return Path(md_file_path).parent / image_path
        with open(markdown.path, "r", encoding="utf-8") as md_file:
            #md_file.__dict__["name"] = markdown.path
            #upload(md_file, new_page, imagePathFunc=convert_image_path, notionPyRendererCls=addHtmlImgTagExtension(NotionPyRenderer))

            new_row: CollectionRowBlock = collection_view.collection.add_row(title=markdown.name)
            new_row.set_property("created_at", markdown.created_at)
            new_row.set_property("modified_at", markdown.modified_at)
            new_row.set_property("Tags", list(map(lambda tag: tag.title(), markdown.tag.split('/'))))

            upload(md_file, new_row)

    # Create database
    def __create_list_collection(self, parent_page: PageBlock):
        collection_view: CollectionViewBlock = parent_page.children.add_new(CollectionViewBlock)
        collection_view.collection = self._client.get_collection(
            self._client.create_record("collection", parent=collection_view, schema=self.__get_collection_schema())
        )
        collection_view.views.add_new(view_type="list")
        collection_view.title = "Notes"
        return collection_view

    def __get_collection_schema(self):
        return {
            "tags": {
                "name": "Tags",
                "type": "multi_select",
                "options": [],
            },
            "created_at": {"name": "Created at", "type": "date"},
            "modified_at": {"name": "Modified at", "type": "date"},
            "title": {"name": "Name", "type": "title"},
        }

    def __print(self, text):
        print(f"[info] {'(dry-run)' if self._dry_run else ''} {text}")
