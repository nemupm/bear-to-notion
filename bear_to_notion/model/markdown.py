from bear_to_notion.model import Model
from pathlib import Path


class Markdown(Model):

    def __init__(self, name: str, tag: str, path: Path, created_at, modified_at):
        super(Markdown, self).__init__()

        # note's name.
        self.name = name
        # hierarchical tag. eg) tech/git
        self.tag = tag
        # markdown file path
        self.path = path

        self.created_at = created_at
        self.modified_at = modified_at
