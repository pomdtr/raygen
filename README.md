# Raygen - Script Generator for [Raycast](https://raycast.com/)

## Installation Guide

```sh
pip install git+https://github.com/pomdtr/raygen.git
```

## Usage

Write a csv or json file listing the title, command and optional description of the scripts.

```csv
title,command
Balance windows size,yabai -m space --balance
Stack on Top of Left,yabai -m window --stack west
Stack on Top of Down,yabai -m window --stack south
Stack on Top of Right,yabai -m window --stack east
Stack on Top of Up,yabai -m window --stack north
```

Run the raygen command `raygen --header-row --output-dir scripts options.csv` to generate a set of scripts:

```console
$ tree scripts
scripts/
├── balance-windows-size.sh
├── stack-on-top-of-down.sh
├── stack-on-top-of-left.sh
├── stack-on-top-of-right.sh
└── stack-on-top-of-up.sh

0 directories, 5 files
```

See the [example](./examples) folder for more illustrated usecases.

## Preview

![example plugin preview](example/preview.png)

## Argument documentation

```console
$ raygen --help
usage: raygen [-h] [--output-dir OUTPUT_DIR] [--clean]
              [--schema-version SCHEMA_VERSION]
              [--mode {silent,compact,fullOutput}] [--package PACKAGE]
              [--icon ICON] [--icon-dark ICON_DARK] [--argument PLACEHOLDER]
              [--encode-arg] [--secure-arg] [--optional-arg]
              [--current-directory-path CURRENT_DIRECTORY_PATH]
              [--needs-confirmation] [--author AUTHOR]
              [--author-url AUTHOR_URL]
              input_csv

Script Generator for Raycast (https://raycast.com/)

positional arguments:
  input_csv             csv describing the title, command and an optional description for each script. Use - to read from stdin.

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output folder of all generated scripts. (default: ./scripts)
  --clean, -r           automatically clean the output folder when it already exists. (default: False)
  --schema-version SCHEMA_VERSION
                        schema version to prepare for future changes in the API.  (default: 1)
  --mode {silent,compact,fullOutput}, -m {silent,compact,fullOutput}
                        specifies how the script is executed and how the output is presented. (default: silent)
  --package PACKAGE     display name of the package that is shown as subtitle in the root search. (default: None)
  --icon ICON           icon that is displayed in the root search (PNG or JPEG). (default: None)
  --icon-dark ICON_DARK
                        same as icon, but for dark theme. If not specified, then icon will be used in both themes. (default: None)
  --argument PLACEHOLDER, -a PLACEHOLDER
  --encode-arg          if you want Raycast to perform percent encoding on the argument value before passing it to the script. (default: False)
  --secure-arg          entered text will be replaced with asterisks and won't be recorded by history. (default: False)
  --optional-arg        if you want to mark the argument as optional. (default: False)
  --current-directory-path CURRENT_DIRECTORY_PATH
                        path from which the script is executed. Default is the path of the script. (default: None)
  --needs-confirmation  show confirmation alert dialog before running the script. (default: False)
  --author AUTHOR       define an author name to be part of the script commands documentation. (default: None)
  --author-url AUTHOR_URL
                        author social media, website, email or anything to help the users to get in touch. (default: None)

Example:

# Simplest usage
raygen options.csv

# Pipe from stdin, add some optional params, clean output dir
cat options.csv | raygen - --package-name Example --icon icon.png --clean

# Add an argument
raygen options.csv --arg queryParam --encode-arg
```
