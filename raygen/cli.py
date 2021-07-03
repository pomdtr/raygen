import argparse
import csv
import pathlib
import shutil
from pathlib import Path
from string import Template
import json
import sys

TEMPLATE = Template(
    """#!/usr/bin/env $shebang
$parameters

$command
"""
)

EXAMPLE_TEXT = """Example:

# Simplest usage
raygen options.json

# Pipe from stdin, add some optional params, clean output dir
cat options.csv | raygen --format csv --package-name Example --icon icon.png --clean -

# Add an argument
raygen options.csv --argument queryParam --encode-arg
"""


def validate_path(path_str):
    path = pathlib.Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{path_str} does not exists!")
    return path


def get_file_and_suffix(path_str):
    path_suffix = None if path_str == "-" else Path(path_str).suffix
    return argparse.FileType("r")(path_str), path_suffix


class SmartFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    "Custom formatter to get both newlines in epilog, and defaults values"


def get_parser():
    PARSER = argparse.ArgumentParser(
        formatter_class=SmartFormatter,
        description="Script Generator for Raycast (https://raycast.com/). See https://github.com/raycast/script-commands for an expansive documentation.",
        epilog=EXAMPLE_TEXT,
    )
    PARSER.add_argument(
        "input",
        help="input file describing the title, command and an optional description for each script. Use - to read from stdin.",
        type=get_file_and_suffix,
    )
    PARSER.add_argument(
        "--input-format", "-f", choices=("csv", "tsv", "json", "ndjson"), help="format of the input"
    )
    PARSER.add_argument(
        "--header-row",
        "-H",
        help="Do not parse the first line as script input",
        action="store_true",
    )
    PARSER.add_argument(
        "--output-dir",
        "-o",
        default="./scripts",
        type=Path,
        help="Output folder of all generated scripts.",
    )
    PARSER.add_argument(
        "--clean",
        "-r",
        action="store_true",
        help="automatically clean the output folder when it already exists.",
    )
    PARSER.add_argument(
        "--schema-version",
        default=1,
        help="schema version to prepare for future changes in the API. ",
    )
    PARSER.add_argument(
        "--mode",
        "-m",
        default="silent",
        choices=["silent", "compact", "fullOutput"],
        help="specifies how the script is executed and how the output is presented.",
    )
    PARSER.add_argument(
        "--package",
        help="display name of the package that is shown as subtitle in the root search.",
    )
    PARSER.add_argument(
        "--icon",
        type=validate_path,
        help="icon that is displayed in the root search (PNG or JPEG).",
    )
    PARSER.add_argument(
        "--icon-dark",
        type=validate_path,
        help="same as icon, but for dark theme. If not specified, then icon will be used in both themes.",
    )
    PARSER.add_argument(
        "--argument",
        "-a",
        metavar="PLACEHOLDER",
        help="add a custom argument to the command",
    )
    PARSER.add_argument(
        "--encode-arg",
        action="store_true",
        help="if you want Raycast to perform percent encoding on the argument value before passing it to the script.",
    )
    PARSER.add_argument(
        "--secure-arg",
        action="store_true",
        help="entered text will be replaced with asterisks and won't be recorded by history.",
    )
    PARSER.add_argument(
        "--optional-arg",
        action="store_true",
        help="if you want to mark the argument as optional.",
    )
    PARSER.add_argument(
        "--current-directory-path",
        help="path from which the script is executed. Default is the path of the script.",
    )
    PARSER.add_argument(
        "--needs-confirmation",
        action="store_true",
        help="show confirmation alert dialog before running the script.",
    )
    PARSER.add_argument(
        "--author",
        help="define an author name to be part of the script commands documentation.",
    )
    PARSER.add_argument(
        "--author-url",
        help="author social media, website, email or anything to help the users to get in touch.",
    )
    PARSER.add_argument(
        "--shebang",
        default="bash",
        help="customize the shebang of the script (Advanced Usage)",
    )
    PARSER.add_argument(
        "--embed",
        type=validate_path,
        action="append",
        help="Include a file in the output folder (can be reapeated)",
    )
    return PARSER


def parse_json_input(file, line_delimited):
    if line_delimited:
        for line in file:
            item = json.loads(line)
            if any(key not in item for key in ("title", "command")):
                raise ValueError("Both title and command title are required")
            yield item
        return
    for item in json.load(file):
        if any(key not in item for key in ("title", "command")):
            raise ValueError("Both title and command title are required")
        yield item


def parse_csv_input(file, header_row, delimiter=","):
    if header_row:
        reader = csv.DictReader(file, delimiter=delimiter)
        if reader.fieldnames is None or any(
            key not in reader.fieldnames for key in ("title", "command")
        ):
            raise ValueError("Both title and command title are required")
        yield from reader
        return
    for row in csv.reader(file, delimiter=delimiter):
        if len(row) < 2:
            raise ValueError("At least two columns are required for each row")
        res = {"title": row[0], "command": row[1]}
        if len(row) > 2:
            res["description"] = row[2]
        yield res


def main():
    args = get_parser().parse_args()

    global_parameters = [
        f"# @raycast.schemaVersion {args.schema_version}",
        f"# @raycast.mode {args.mode}",
    ]

    if args.needs_confirmation:
        global_parameters.append("# @raycast.needsConfirmation true")
    if args.package:
        global_parameters.append(f"# @raycast.packageName {args.package}")
    if args.current_directory_path:
        global_parameters.append(
            f"# @raycast.currentDirectoryPath {args.current_directory_path}"
        )
    if args.author_url:
        global_parameters.append(f"# @raycast.authorURL {args.author_url}")
    if args.needs_confirmation:
        global_parameters.append(f"# @raycast.needsConfirmation true")

    if args.argument:
        options = {
            "type": "text",
            "placeholder": args.argument,
            "percentEncoded": args.encode_arg,
            "optional": args.optional_arg,
            "secure": args.secure_arg,
        }
        global_parameters.append(f"# @raycast.argument1 {json.dumps(options)}")

    input_file, input_suffix = args.input

    if args.input_format:
        input_format = args.input_format
    elif input_suffix:
        input_format = input_suffix[1:].lower()
    else:
        raise Exception
    if input_format == "csv":
        items = parse_csv_input(input_file, args.header_row)
    elif input_format == "tsv":
        items = parse_csv_input(input_file, args.header_row, delimiter="\t")
    elif input_format == "json":
        items = parse_json_input(input_file, line_delimited=False)
    elif input_format == "ndjson":
        items = parse_json_input(input_file, line_delimited=True)
    else:
        print(f"Unknown format : {args.input_format}")
        sys.exit(1)

    if args.clean and args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.icon:
        filename = args.icon.name
        shutil.copy(args.icon, args.output_dir / filename)
        global_parameters.append(f"# @raycast.icon {filename}")

    if args.icon_dark:
        filename = args.dark_icon.name
        shutil.copy(args.icon_dark, args.output_dir / filename)
        global_parameters.append(f"# @raycast.iconDark {filename}")

    for embed in args.embed:
        shutil.copy(embed, args.output_dir / embed.name)

    for item in items:
        filename = item["title"].replace(" ", "-").lower() + ".sh"
        script_parameters = [
            *global_parameters,
            f"# @raycast.title {item['title']}",
        ]
        if item.get("description"):
            script_parameters.append(f"# @raycast.description {item['description']}")

        with open(args.output_dir / filename, "w") as fh:
            fh.write(
                TEMPLATE.safe_substitute(
                    title=item["title"],
                    command=item["command"],
                    parameters="\n".join(script_parameters),
                    shebang=args.shebang,
                )
            )

if __name__ == "__main__":
    main()
