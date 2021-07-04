from typing import List, Union
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from pathlib import Path
from string import Template

TEMPLATE = Template(
    """#!/usr/bin/env $shebang
$parameters

$command
"""
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RaycastArgument:
    placeholder: str
    percent_encoded: bool = False
    secure: bool = False
    optional: bool = False
    type: str = "text"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RaycastItem():
    title: Union[str, None] = None
    command: Union[str, None] = None
    mode: str = "silent"
    schema_version: int = 1
    package_name: Union[str, None] = None
    author: Union[str, None] = None
    author_url: Union[str, None] = None
    description: Union[str, None] = None
    needs_confirmation: bool = False
    current_directory_path: Union[str, None] = None
    arguments: List[RaycastArgument] = field(default_factory=list)
    icon: Union[str, None] = None
    icon_dark: Union[str, None] = None
    refresh_time: Union[str, None] = None

    @staticmethod
    def from_cli(args):
        return RaycastItem(
            mode=args.mode,
            schema_version=args.schema_version,
            package_name=args.package_name,
            author=args.author,
            needs_confirmation=args.needs_confirmation,
            current_directory_path=args.current_directory_path,
            arguments=[] if not args.argument else [RaycastArgument(args.argument, args.encode_arg, args.secure_arg, args.optional_arg)],
            icon=args.icon,
            icon_dark=args.icon_dark,
            refresh_time=args.refresh_time
        )

    def apply_defaults(self, defaults: "RaycastItem"):
        return RaycastItem(
            title = self.title or defaults.title,
            command=self.command or defaults.command,
            schema_version = self.schema_version or defaults.schema_version,
            mode = self.mode or defaults.mode,
            package_name = self.package_name or defaults.package_name,
            author = self.author or defaults.author,
            author_url = self.author_url or defaults.author_url,
            arguments = self.arguments or defaults.arguments,
            description = self.description or defaults.description,
            needs_confirmation = self.needs_confirmation or defaults.needs_confirmation,
            current_directory_path = self.current_directory_path or defaults.current_directory_path,
            icon = self.icon or defaults.icon,
            icon_dark = self.icon_dark or defaults.icon_dark,
            refresh_time= self.refresh_time or defaults.refresh_time
        )

    def build_script(self, shebang):
        if self.title is None:
            raise Exception
        script_parameters = [
            f"# @raycast.schemaVersion {self.schema_version}",
            f"# @raycast.mode {self.mode}",
            f"# @raycast.title {self.title}",
        ]
        if self.package_name:
            script_parameters.append(
                f"# @raycast.packageName {self.package_name}"
            )
        if self.author:
            script_parameters.append(f"# @raycast.author {self.author}")
        if self.author_url:
            script_parameters.append(f"# @raycast.authorURL {self.author_url}")
        for i, arg in enumerate(self.arguments, 1):
            script_parameters.append(f"# @raycast.argument{i} {arg.to_json()}")

        if self.description:
            script_parameters.append(
                f"# @raycast.description {self.description}"
            )
        if self.needs_confirmation:
            script_parameters.append("# @raycast.needsConfirmation true")

        if self.current_directory_path:
            script_parameters.append(
                f"# @raycast.currentDirectoryPath {self.current_directory_path}"
            )

        if self.icon:
            script_parameters.append(f"# @raycast.icon {Path(self.icon).name}")

        if self.icon_dark:
            script_parameters.append(f"# @raycast.iconDark {Path(self.icon_dark).name}")

        if self.refresh_time:
            script_parameters.append(f"# @raycast.refreshTime {self.refresh_time}")

        return  TEMPLATE.safe_substitute(
                    title=self.title,
                    command=self.command,
                    parameters="\n".join(script_parameters),
                    shebang=shebang,
                )

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RaygenParams():
    output_dir: str = ""
    clean: bool = False
    embeds: List[str] = field(default_factory=list)
    shebang: str = ""
    defaults: RaycastItem = field(default_factory=RaycastItem)
    items: List[RaycastItem] = field(default_factory=list)

    @staticmethod
    def from_cli(args):
        return RaygenParams(
            output_dir=args.output_dir,
            clean=args.clean,
            embeds=args.embed,
            shebang=args.shebang,
            defaults=RaycastItem.from_cli(args)
        )

    def apply_defaults(self, defaults: "RaygenParams"):
        return RaygenParams(
            output_dir=self.output_dir or defaults.output_dir,
            clean=self.clean or defaults.clean,
            embeds=self.embeds or defaults.embeds,
            shebang=self.shebang or defaults.shebang,
            defaults=self.defaults.apply_defaults(defaults.defaults),
            items=self.items or defaults.items
        )

    def get_items(self):
        return [item.apply_defaults(self.defaults) for item in self.items]


