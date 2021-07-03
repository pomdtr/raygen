import argparse
import pathlib
from pathlib import Path

from raygen.io import generate_scripts, parse_items

EXAMPLE_TEXT = """Example:

# Simplest usage
raygen options.json

# Pipe from stdin, add some optional params, clean output dir
cat options.csv | raygen --format csv --package-name Example --icon icon.png --clean -

# Add an argument
raygen options.csv --argument queryParam --encode-arg
"""


def valid_path(path_str):
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
        "--input-format",
        "-f",
        choices=("csv", "tsv", "json", "ndjson"),
        help="format of the input",
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
        "--package-name",
        help="display name of the package that is shown as subtitle in the root search.",
    )
    PARSER.add_argument(
        "--icon",
        type=valid_path,
        help="icon that is displayed in the root search (PNG or JPEG).",
    )
    PARSER.add_argument(
        "--icon-dark",
        type=valid_path,
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
        type=valid_path,
        default=[],
        action="append",
        help="Include a file in the output folder (can be reapeated)",
    )
    return PARSER


def main():
    args = get_parser().parse_args()
    arg_dict = vars(args)

    input_file, input_suffix = arg_dict.pop("input")
    raygen_params, raycast_params, raycast_items = parse_items(
        input_file, input_suffix, arg_dict
    )

    generate_scripts(
        raygen_params.output_dir,
        raycast_params,
        raycast_items,
        clean=raygen_params.clean,
        embeds=raygen_params.embeds,
        shebang=raygen_params.shebang,
    )


if __name__ == "__main__":
    main()
