from typing import List, Union
from dataclasses import dataclass, field


@dataclass
class RaycastArgument:
    placeholder: str
    percent_encoded: bool
    secure: bool
    optional: bool


@dataclass
class RaycastParams:
    mode: str
    schema_version: int = 1
    package_name: Union[str, None] = None
    author: Union[str, None] = None
    author_url: Union[str, None] = None


@dataclass
class RaycastItem:
    title: str
    command: str
    description: Union[str, None] = None
    needs_confirmation: bool = False
    current_directory_path: Union[str, None] = None
    arguments: List[RaycastArgument] = field(default_factory=list)
    icon: Union[str, None] = None
    icon_dark: Union[str, None] = None


@dataclass
class RaygenParams:
    output_dir: str
    clean: bool
    embeds: List[str]
    shebang: str
