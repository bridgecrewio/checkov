import asyncio
import json
import logging
import os
import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Tuple, Dict, Any

from aiomultiprocess import Pool

from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.vulnerability_scanning.integrations.package_scanning import package_scanning_integration


TWISTCLI_FILE_NAME = 'twistcli'
CHECKOV_SEC_IN_WEEK = 604800


class Scanner:
    def __init__(self) -> None:
        self.twistcli_path = Path(bridgecrew_dir) / TWISTCLI_FILE_NAME

    def setup_twictcli(self) -> None:
        try:
            if self.should_download():
                if not os.path.exists(bridgecrew_dir):
                    os.makedirs(bridgecrew_dir)
                self.cleanup_twictcli()
                package_scanning_integration.download_twistcli(self.twistcli_path)
        except Exception:
            logging.error("Failed to setup twictcli for package scanning", exc_info=True)
            raise

    def should_download(self) -> bool:
        if not self.twistcli_path.exists():
            return True
        last_modification = os.stat(self.twistcli_path)
        file_age = (time.time() - last_modification.st_mtime)
        return file_age >= int(os.getenv("CHECKOV_EXPIRATION_TIME_IN_SEC", CHECKOV_SEC_IN_WEEK))

    def cleanup_twictcli(self) -> None:
        if self.twistcli_path.exists():
            self.twistcli_path.unlink()
            logging.info('twistcli file removed')

    def scan(self, input_output_paths: "Iterable[Tuple[Path, Path]]", cleanup_twictcli: bool = False) \
            -> "Sequence[Dict[str, Any]]":
        self.setup_twictcli()

        scan_results = asyncio.run(
            self.run_scan_multi(
                address=package_scanning_integration.get_proxy_address(),
                bc_api_key=package_scanning_integration.get_bc_api_key(),
                input_output_paths=input_output_paths,
            )
        )
        if cleanup_twictcli:
            self.cleanup_twictcli()
        return scan_results

    async def run_scan_multi(
        self,
        address: str,
        bc_api_key: str,
        input_output_paths: "Iterable[Tuple[Path, Path]]",
    ) -> "Sequence[Dict[str, Any]]":
        args = [
            (
                f"{self.twistcli_path} coderepo scan --address {address} --token {bc_api_key} --output-file '{output_path.absolute()}' '{input_path.absolute()}'",
                input_path,
                output_path,
            )
            for input_path, output_path in input_output_paths
        ]
        if os.getenv("PYCHARM_HOSTED") == "1":
            # PYCHARM_HOSTED env variable equals 1 when running via Pycharm.
            # it avoids us from crashing, which happens when using multiprocessing via Pycharm's debug-mode
            logging.warning("Running the scans in sequence for avoiding crashing when running via Pycharm")
            scan_results = []
            for curr_arg in args:
                scan_results.append(await self.run_scan(*curr_arg))
        else:
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
    
    
