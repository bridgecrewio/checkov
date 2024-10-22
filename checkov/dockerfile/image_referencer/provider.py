from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, Any

from checkov.common.images.image_referencer import Image
from checkov.common.util.str_utils import removeprefix
from checkov.dockerfile.utils import DOCKERFILE_STARTLINE, DOCKERFILE_ENDLINE

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class DockerfileProvider:
    __slots__ = ("definitions",)

    def __init__(self, definitions: dict[str, dict[str, list[_Instruction]]]) -> None:
        self.definitions = definitions

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        for file_path, config in self.definitions.items():
            instructions = config.get("FROM")
            if not isinstance(instructions, list):
                continue

            # just scan the last one
            instruction = instructions[-1]

            name = instruction["value"]

            if name.startswith("--platform"):
                # indicates a multi-platform build, therefore skip it
                # ex. FROM --platform=$BUILDPLATFORM golang:alpine AS build
                continue

            if " AS " in name:
                # indicates a multi-stage build, therefore remove everything starting from AS
                # ex. FROM amazonlinux:2 as run
                name = name.split(" AS ")[0]

            file_path = f'{removeprefix(file_path, os.getenv("BC_ROOT_DIR", ""))}'
            images.append(
                Image(
                    file_path=file_path,
                    name=name,
                    start_line=instruction[DOCKERFILE_STARTLINE] + 1,  # starts with 0
                    end_line=instruction[DOCKERFILE_ENDLINE] + 1,
                    related_resource_id=f'{file_path}:{file_path}.FROM',
                )
            )

        return images
