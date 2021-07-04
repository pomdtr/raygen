import csv
import shutil
import sys
from pathlib import Path
from typing import List
import re

from raygen.models import (RaycastItem,
                           RaygenParams)

def ndjson_loader(file):
    return [RaycastItem.from_json(line) for line in file]

def parse_json_input(file, line_delimited) -> RaygenParams:
    if line_delimited:
        return RaygenParams(items=list(ndjson_loader(file)))
    return RaygenParams.from_json(file.read())

def parse_csv_input(file, header_row, delimiter=",") -> List[RaycastItem]:
    if header_row:
        reader = csv.DictReader(file, delimiter=delimiter)
        if reader.fieldnames is None or any(
            key not in reader.fieldnames for key in ("title", "command")
        ):
            raise ValueError("Both title and command title are required")
        for row in reader:
            yield RaycastItem(**row)
    for row in csv.reader(file, delimiter=delimiter):
        if len(row) != 2:
            raise ValueError("At least two columns are required for each row")
        yield RaycastItem(title=row[0], command=row[1])

def parse_items(
    args
) -> RaygenParams:
    input_file, input_suffix = args.input
    input_format = args.input_format or input_suffix
    header_row = args.header_row
    cli_params = RaygenParams.from_cli(args)

    if input_format == "csv":
        raycast_items = list(parse_csv_input(input_file, header_row))
        cli_params.items = raycast_items
        return cli_params
    elif input_format == "tsv":
        raycast_items = list(parse_csv_input(input_file, header_row, delimiter="\t"))
        cli_params.items = raycast_items
        return cli_params
    elif input_format == "json":
        json_params = parse_json_input(input_file, line_delimited=False)
        return json_params.apply_defaults(cli_params)
    elif input_format == "ndjson":
        json_params = parse_json_input(input_file, line_delimited=True)
        return json_params.apply_defaults(cli_params)
    else:
        # TODO
        print(f"Unknown format : {input_format}")
        sys.exit(1)


def copy(filepath, output_dir):
    filepath = Path(filepath)
    output_dir = Path(output_dir)
    if not filepath.exists():
        raise FileExistsError
    shutil.copy(filepath, output_dir / filepath.name)


def generate_scripts(
    raycast_items: List[RaycastItem], output_dir="./scripts", clean=False, shebang="bash", embeds=[]
):
    """Generate one script for each provided item in the output folder

    Args:
        raycast_items (List[RaycastItem]): items params will be used as script directives
        output_dir (str, optional): directory were all scripts will be stored. Defaults to "./scripts".
        clean (bool, optional): if set, the output directory will be cleaned before any scripts generation. Defaults to False.
        shebang (str, optional): shebang of the output scripts. Defaults to "bash".
        embeds (list, optional): path to files to embed in the output dir. Usefull when you want to reference another script. Defaults to [].
    """
    output_dir = Path(output_dir)
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for embed in embeds:
        copy(embed, output_dir)

    for raycast_item in raycast_items:
        if not raycast_item.title:
            raise ValueError("Title should be provided for each item")
        filename = raycast_item.title.replace(" ", "_").replace("/", "-").lower() + ".sh"
        filename = re.sub(r"[\s/.]+", "-", raycast_item.title).lower() + "." + shebang

        if raycast_item.icon:
            copy(raycast_item.icon, output_dir)
        if raycast_item.icon_dark:
            copy(raycast_item.icon_dark, output_dir)

        with open(Path(output_dir) / filename, "w") as fh:
            fh.write(
                raycast_item.build_script(shebang)
            )
