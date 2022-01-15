#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.dirname(os.path.join(os.getcwd(), os.pardir)))
from bear_to_notion.client import Client
import click

@click.group()
def command():
    pass

@command.command()
@click.option('--bearbk-path', help="unzipped bearbk path")
@click.option('--notion-token', help="notion's token")
@click.option('--root', help="url of root page where md files are added")
@click.option('-x', '--disallowed-tag', multiple=True, help="tags which shouldn't be imported to notion")
@click.option('--dry-run/--no-dry-run', default=True)
def run(bearbk_path, notion_token, root, disallowed_tag, dry_run):
    disallowed_tags = []
    if disallowed_tag is not None:
        disallowed_tags = disallowed_tag
    client = Client('importer', {
        'bearbk_path': bearbk_path,
        'notion_token': notion_token,
        'root': root,
        'disallowed_tags': disallowed_tags,
        'dry_run': dry_run,
    })
    client.run()

def main():
    command()

if __name__ == '__main__':
    main()
