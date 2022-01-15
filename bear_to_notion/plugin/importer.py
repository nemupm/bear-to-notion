from bear_to_notion.plugin import Plugin
from bear_to_notion.service.bear import Bear
from bear_to_notion.service.notion_uploader import NotionUploader

class Importer(Plugin):
    def __init__(self, options):
        super(Importer, self).__init__(options)
        self.bear = Bear(options['bearbk_path'])
        self.notion = NotionUploader(options['root'], options['notion_token'], options['disallowed_tags'], options['dry_run'])

    def run(self):
        self.notion.upload(self.bear.markdown_files)

def plugin_instance(options):
    return Importer(options)
