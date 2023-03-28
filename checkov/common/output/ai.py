from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

import openai
from termcolor import colored

from checkov.common.bridgecrew.check_type import CheckType

if TYPE_CHECKING:
    from checkov.common.output.record import Record

OPENAI_API_KEY = os.getenv("CKV_OPENAI_API_KEY")
OPENAI_MAX_FINDINGS = int(os.getenv("CKV_OPENAI_MAX_FINDINGS", 5))
OPENAI_MAX_TOKENS = int(os.getenv("CKV_OPENAI_MAX_TOKENS", 512))
OPENAI_MODEL = os.getenv("CKV_OPENAI_MODEL", "gpt-3.5-turbo")

RUNNER_DENY_LIST = {
    CheckType.POLICY_3D,
    CheckType.SCA_IMAGE,
    CheckType.SCA_PACKAGE,
    CheckType.SECRETS,
}


class OpenAi:
    def __init__(self) -> None:
        self._should_run = False

        if OPENAI_API_KEY:
            self._should_run = True
            openai.api_key = OPENAI_API_KEY

    def enhance_records(self, runner_type: str, records: list[Record]) -> None:
        if not self._should_run:
            return
        if runner_type in RUNNER_DENY_LIST:
            return

        asyncio.run(self._generate_guidelines(records=records))

    async def _generate_guidelines(self, records: list[Record]) -> None:
        enhance_records = self._prioritize_findings(records=records)

        batches = [enhance_records]
        if len(enhance_records) > 20:
            # https://platform.openai.com/docs/guides/rate-limits/what-are-the-rate-limits-for-our-api
            # for free users 20 RPM is the limit, therefore splitting into batches of 10
            batch_size = 10
            batches = [records[i : i + batch_size] for i in range(0, len(enhance_records), batch_size)]

        self._print_warning(
            records_count=len(records),
            enhance_records_count=len(enhance_records),
            batches_count=len(batches),
        )

        for batch in batches:
            await asyncio.gather(*[self._chat_complete(record=record) for record in batch])

    async def _chat_complete(self, record: Record) -> None:
        if not record.code_block:
            # no need to ask OpenAI about guidelines, if we have no code blocks
            return

        completion = await openai.ChatCompletion.acreate(  # type:ignore[no-untyped-call]
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a security tool"},
                {
                    "role": "user",
                    "content": "".join(
                        [
                            f"fix following code, which violates checkov policy '{record.check_name}':\n",
                            *[line for _, line in record.code_block],
                        ]
                    ),
                },
                {"role": "user", "content": "Explain"},
            ],
            temperature=0,
            max_tokens=OPENAI_MAX_TOKENS,
        )
        logging.info(f"OpenAI request consumed {completion.usage.total_tokens} tokens")

        details = self._parse_completion_response(completion_content=completion.choices[0].message.content)
        if details:
            record.details = details

    def _prioritize_findings(self, records: list[Record]) -> list[Record]:
        if 0 < OPENAI_MAX_FINDINGS < len(records):
            # the higher severities should be preferred
            records = sorted(records, key=lambda record: record.severity.level if record.severity else 0, reverse=True)

            # to protect user, just take the first x findings
            return records[:OPENAI_MAX_FINDINGS]

        return records

    def _parse_completion_response(self, completion_content: str) -> list[str]:
        result = []

        if completion_content:
            result.append("The following text is AI generated therefore treat with caution.")
            result.append("")

        code = False
        for line in completion_content.splitlines():
            if "```" in line:
                if code:
                    code = False
                else:
                    code = True
                continue
            if code:
                result.append(line)
            elif not line:
                result.append(line)
            else:
                result.extend(
                    sentence if sentence.endswith((".", ":")) else f"{sentence}."
                    for sentence in line.strip().split(". ")
                )

        return result

    def _print_warning(self, records_count: int, enhance_records_count: int, batches_count: int) -> None:
        max_findings_note = ""
        if 0 < OPENAI_MAX_FINDINGS < records_count:
            max_findings_note = (
                f"Found in total {records_count} failed checks. To add enhanced guidelines to all of them,\n"
                "please adjust the env var 'CKV_OPENAI_MAX_FINDINGS' accordingly or set 0 to enhance all.\n"
            )

        print(
            colored(
                f"WARNING: About to request {enhance_records_count} enhanced guidelines within the next {batches_count * 15}s.\n{max_findings_note}",
                "yellow",
            )
        )


open_ai = OpenAi()
