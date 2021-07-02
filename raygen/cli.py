import argparse
import csv
import pathlib
import shutil
from pathlib import Path
from string import Template
import json

TEMPLATE = Template(
"""#!/usr/bin/env bash
$parameters

$command
"""
)

EXAMPLE_TEXT = """Example:

# Simplest usage
raygen options.csv

# Pipe from stdin, add some optional params, clean output dir
cat options.csv | raygen - --package-name Example --icon icon.png --clean

# Add an argument
raygen options.csv --argument queryParam --encode-arg
"""

def real_path(path_string):
    path = pathlib.Path(path_string)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{path_string} does not exists!")
    return path

class SmartFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    "Custom formatter to get both newlines in epilog, and defaults values"


PARSER = argparse.ArgumentParser(formatter_class=SmartFormatter, description="Script Generator for Raycast (https://raycast.com/). See https://github.com/raycast/script-commands for an expansive documentation.", epilog=EXAMPLE_TEXT)
PARSER.add_argument("input_csv", help="csv describing the title, command and an optional description for each script. Use - to read from stdin.", type=argparse.FileType('r'))
PARSER.add_argument("--output-dir", "-o", default="./scripts", type=Path, help="Output folder of all generated scripts.")
PARSER.add_argument("--clean", "-r", action="store_true", help="automatically clean the output folder when it already exists.")
PARSER.add_argument("--schema-version", default=1, help="schema version to prepare for future changes in the API. ")
PARSER.add_argument("--mode", "-m", default="silent", choices=["silent", "compact", "fullOutput"], help="specifies how the script is executed and how the output is presented.")
PARSER.add_argument("--package", help="display name of the package that is shown as subtitle in the root search.")
PARSER.add_argument("--icon", type=real_path, help="icon that is displayed in the root search (PNG or JPEG).")
PARSER.add_argument("--icon-dark", type=real_path, help="same as icon, but for dark theme. If not specified, then icon will be used in both themes.")
PARSER.add_argument("--argument", "-a", metavar="PLACEHOLDER", help="add a custom argument to the command")
PARSER.add_argument("--encode-arg", action="store_true", help="if you want Raycast to perform percent encoding on the argument value before passing it to the script.")
PARSER.add_argument("--secure-arg", action="store_true", help="entered text will be replaced with asterisks and won't be recorded by history.")
PARSER.add_argument("--optional-arg", action="store_true", help="if you want to mark the argument as optional.")
PARSER.add_argument("--current-directory-path", help="path from which the script is executed. Default is the path of the script.")
PARSER.add_argument("--needs-confirmation", action="store_true", help="show confirmation alert dialog before running the script.")
PARSER.add_argument("--author", help="define an author name to be part of the script commands documentation.")
PARSER.add_argument("--author-url", help="author social media, website, email or anything to help the users to get in touch.")

def main():
    args = PARSER.parse_args()

    if args.clean and args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    global_parameters = [
        f"# @raycast.schemaVersion {args.schema_version}",
        f"# @raycast.needsConfirmation {json.dumps(args.needs_confirmation)}",
        f"# @raycast.mode {args.mode}",
    ]

    if args.package:
        global_parameters.append(f"# @raycast.packageName {args.package}")
    if args.current_directory_path:
        global_parameters.append(f"# @raycast.currentDirectoryPath {args.current_directory_path}")
    if args.author_url:
        global_parameters.append(f"# @raycast.authorURL {args.author_url}")
    if args.needs_confirmation:
        global_parameters.append(f"# @raycast.needsConfirmation true")


    if args.argument:
        options = {
            "type": "text",
            "placeholder": args.argument,
            "percentEncoded": args.encode,
            "optional": args.optional,
            "secure": args.secure
        }
        global_parameters.append(
            f"# @raycast.argument1 {json.dumps(options)}"
        )


    if args.icon:
        filename = args.icon.name
        shutil.copy(args.icon, args.output_dir / filename)
        global_parameters.append(f"# @raycast.icon {filename}")

    if args.icon_dark:
        shutil.copy(args.icon_dark, args.output_dir / "iconDark")
        global_parameters.append(f"# @raycast.iconDark ./iconDark")


    lines = csv.DictReader(args.input_csv)

    for line in lines:
        filename = line["title"].replace(" ", "-").lower() + ".sh"
        script_parameters = [
            *global_parameters,
            f"# @raycast.title {line['title']}",
        ]
        description = line.get('description')
        if description:
            script_parameters.append(f"# @raycast.description {line['description']}")

        with open(args.output_dir / filename, "w") as fh:
            fh.write(
                TEMPLATE.safe_substitute(title=line["title"], command=line["command"], parameters="\n".join(script_parameters))
            )

if __name__ == "__main__":
    main()
