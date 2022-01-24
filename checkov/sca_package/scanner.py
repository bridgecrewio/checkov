import asyncio
import json
import logging
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Tuple, Dict, Any

from aiomultiprocess import Pool

from checkov.common.bridgecrew.vulnerability_scanning.integrations.package_scanning import package_scanning_integration
from checkov.common.bridgecrew.vulnerability_scanning.package_scanner import TWISTCLI_FILE_NAME, PackageScanner


class Scanner:
    def scan(self, input_output_paths: "Iterable[Tuple[Path, Path]]") -> "Sequence[Dict[str, Any]]":
        package_scanner = PackageScanner()

        package_scanner.setup_scan()

        scan_results = asyncio.run(
            self.run_scan_multi(
                address=package_scanning_integration.get_proxy_address(),
                bc_api_key=package_scanning_integration.get_bc_api_key(),
                input_output_paths=input_output_paths,
            )
        )

        return scan_results

    async def run_scan_multi(
        self,
        address: str,
        bc_api_key: str,
        input_output_paths: "Iterable[Tuple[Path, Path]]",
    ) -> "Sequence[Dict[str, Any]]":
        args = [
            (
                f"./{TWISTCLI_FILE_NAME} coderepo scan --address {address} --token {bc_api_key} --output-file '{output_path.absolute()}' '{input_path.absolute()}'",
                input_path,
                output_path,
            )
            for input_path, output_path in input_output_paths
        ]
        async with Pool() as pool:
            scan_results = await pool.starmap(self.run_scan, args)

        return scan_results

    async def run_scan(
        self,
        command: str,
        input_path: Path,
        output_path: Path,
    ) -> Dict[str, Any]:
        logging.info(f"Start to scan package file {input_path}")
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # log output for debugging
        logging.debug(stdout.decode())

        exit_code = await process.wait()

        if exit_code:
            logging.error(f"Failed to scan package file {input_path}")
            logging.error(stderr.decode())
            return {}

        logging.info(f"Successfully scanned package file {input_path}")

        # read and delete the report file
        scan_result = json.loads(output_path.read_text())
        output_path.unlink()

        return scan_result
