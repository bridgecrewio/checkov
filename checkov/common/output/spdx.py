from __future__ import annotations

from io import StringIO

from spdx.creationinfo import Tool, Organization
from spdx.document import Document
from spdx.license import License
from spdx.writers.tagvalue import write_document

from checkov.common.output.report import Report

DOCUMENT_NAME = "checkov-sbom"


class SPDX:
    def __init__(self, repo_id: str | None, reports: list[Report]):
        self.repo_id = f"{repo_id}/" if repo_id else ""
        self.reports = reports

        self.document = self.create_document()

    def create_document(self) -> Document:
        document = Document(
            version="SPDX2.3",
            data_license=License.from_identifier(identifier="CC0-1.0"),
            name=DOCUMENT_NAME,
            spdx_id="SPDXRef-DOCUMENT",
            namespace=f"{self.repo_id}{DOCUMENT_NAME}",
        )
        document.creation_info.set_created_now()
        document.creation_info.add_creator(Tool(name="checkov"))
        document.creation_info.add_creator(Organization(name="bridgecrew"))

        return document

    def get_tag_value_output(self) -> str:
        output = StringIO()

        write_document(document=self.document, out=output, validate=False)  # later set to True

        return output.getvalue()
