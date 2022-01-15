Importer from Bear to Notion
=====================================

Unofficial script to import md files from Bear to Notion.

Requirements
---------------
* Python(3.9)

Example
---------------
::

    $ bear-to-notion run \
        --disallowed-tag "sensitive information" \
        --bearbk-path "/Bear Notes 2022-01-01 at 12.01.bearbk" \
        --notion-token "xxx" \
        --root "https://www.notion.so/Notes-xxxxx" \
        |grep -v "not supported in Notion.so, converting to" |grep -v "has no corresponding syntax in Notion.so"

Installation
---------------
::

    $ python setup.py sdist
    $ pip uninstall bear-to-notion # if already installed
    $ pip install dist/bear-to-notion-0.0.1.tar.gz

Usage
---------------

run
""""""""""
::

    $ bear-to-notion run --help
    Usage: bear-to-notion run [OPTIONS]

    Options:
      --bearbk-path TEXT         unzipped bearbk path
      --notion-token TEXT        notion's token
      --root TEXT                url of root page where md files are added
      -x, --disallowed-tag TEXT  tags which shouldn't be imported to notion
      --dry-run / --no-dry-run
      --help                     Show this message and exit.

Note
---------------
* You may have to modify BEAR_TAG_PATTERN.
* Uploading media files are not supported.
*
