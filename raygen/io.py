import csv
import json
import shutil
import sys
from pathlib import Path
from string import Template
from typing import List, Tuple

from raygen.models import (RaycastArgument, RaycastItem, RaycastParams,
                           RaygenParams)
from raygen.utils import complete_dict, snake_case

TEMPLATE = Template(
    """#!/usr/bin/env $shebang
$parameters

$command
"""
)


def ndjson_loader(file):
    for line in file:
        item = json.loads(line)
        if any(key not in item for key in ("title", "command")):
            raise ValueError("Both title and command title are required")
        yield RaycastItem(**item)


def parse_json_input(file, line_delimited):
    if line_delimited:
        return ndjson_loader(file), {}, {}
    json_object = json.load(file)
    items = json_object.pop("items")
    params = json_object.pop("params", {})
    return (
        [RaycastItem(**item) for item in items],
        {snake_case(key): value for key, value in params.items()},
        {snake_case(key): value for key, value in json_object.items()},
    )


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
        if len(row) < 2:
            raise ValueError("At least two columns are required for each row")
        res = {"title": row[0], "command": row[1]}
        if len(row) > 2:
            res["description"] = row[2]
        yield RaycastItem(**res)


def parse_items(
    args
) -> Tuple[RaygenParams, RaycastParams, List[RaycastItem]]:
    input_file, input_suffix = args.input
    input_format = args.input_format or input_suffix
    raycast_additional_args = {}
    raygen_additional_args = {}
    header_row = args.header_row
    if input_format == "csv":
        raycast_items = parse_csv_input(input_file, header_row)
    elif input_format == "tsv":
        raycast_items = parse_csv_input(input_file, header_row, delimiter="\t")
    elif input_format == "json":
        (
            raycast_items,
            raycast_additional_args,
            raygen_additional_args,
        ) = parse_json_input(input_file, line_delimited=False)
    elif input_format == "ndjson":
        (
            raycast_items,
            raycast_additional_args,
            raygen_additional_args,
        ) = parse_json_input(input_file, line_delimited=True)
    else:
        print(f"Unknown format : {input_format}")
        sys.exit(1)

    raygen_args = complete_dict(
        {
            "clean": args.clean,
            "output_dir": args.output_dir,
            "embeds": args.embed,
            "shebang": args.shebang,
        },
        raygen_additional_args,
    )
    raycast_items = list(raycast_items)

    complete_items(raycast_items, args)
    raycast_args = complete_dict(
        {
            "schema_version": args.schema_version,
            "mode": args.mode,
            "package_name": args.package_name,
            "author": args.author,
            "author_url": args.author_url,
        },
        raycast_additional_args,
    )

    return (
        RaygenParams(**raygen_args),
        RaycastParams(**raycast_args),
        raycast_items,
    )


def complete_items(items: List[RaycastItem], args):
    argument = None
    if args.argument:
        argument = RaycastArgument(
            placeholder=args.argument,
            percent_encoded=args.encode_arg,
            secure=args.secure_arg,
            optional=args.optional_arg,
        )
    for item in items:
        if argument:
            item.arguments = [argument]
        if args.needs_confirmation:
            item.needs_confirmation = args.needs_confirmation
        if args.current_directory_path:
            item.current_directory_path = args.current_directory_path
        if args.icon:
            item.icon = args.icon
        if args.icon_dark:
            item.icon_dark = args.icon_dark


def generate_scripts(
    output_dir,
    raycast_params: RaycastParams,
    raycast_items: List[RaycastItem],
    clean=False,
    embeds=[],
    shebang="bash",
):
    output_dir = Path(output_dir)
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for embed in embeds:
        embed = Path(embed)
        if not embed.exists():
            raise FileExistsError(f"File {embed} does not exists")
        shutil.copy(embed, output_dir / embed.name)

    global_parameters = [
        f"# @raycast.schemaVersion {raycast_params.schema_version}",
        f"# @raycast.mode {raycast_params.mode}",
    ]
    if raycast_params.package_name:
        global_parameters.append(
            f"# @raycast.packageName {raycast_params.package_name}"
        )
    if raycast_params.author:
        global_parameters.append(f"# @raycast.author {raycast_params.author}")
    if raycast_params.author_url:
        global_parameters.append(f"# @raycast.authorURL {raycast_params.author_url}")

    for raycast_item in raycast_items:
        filename = raycast_item.title.replace(" ", "-").lower() + ".sh"
        script_parameters = [
            *global_parameters,
            f"# @raycast.title {raycast_item.title}",
        ]
        for i, arg in enumerate(raycast_item.arguments, 1):
            options = {
                "type": "text",
                "placeholder": arg.placeholder,
                "percentEncoded": arg.percent_encoded,
                "optional": arg.optional,
                "secure": arg.secure,
            }
            script_parameters.append(f"# @raycast.argument{i} {json.dumps(options)}")

        if raycast_item.description:
            script_parameters.append(
                f"# @raycast.description {raycast_item.description}"
            )
        if raycast_item.needs_confirmation:
            global_parameters.append("# @raycast.needsConfirmation true")

        if raycast_item.current_directory_path:
            script_parameters.append(
                f"# @raycast.currentDirectoryPath {raycast_item.current_directory_path}"
            )

        if raycast_item.icon:
            icon_path = Path(raycast_item.icon)
            dest_path = output_dir / icon_path.name
            if not dest_path.exists():
                shutil.copy(icon_path, dest_path)
            script_parameters.append(f"# @raycast.icon {icon_path.name}")

        if raycast_item.icon_dark:
            icon_path = Path(raycast_item.icon_dark)
            dest_path = output_dir / icon_path.name
            if not dest_path.exists():
                shutil.copy(icon_path, dest_path)
            script_parameters.append(f"# @raycast.iconDark {icon_path.name}")

        with open(Path(output_dir) / filename, "w") as fh:
            fh.write(
                TEMPLATE.safe_substitute(
                    title=raycast_item.title,
                    command=raycast_item.command,
                    parameters="\n".join(script_parameters),
                    shebang=shebang,
                )
            )
