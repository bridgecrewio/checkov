import os
import json

from checkov.common.sast.consts import SastLanguages


class FilesFilterManager:
    def __init__(self, source_codes, languages) -> None:
        self.source_codes = source_codes
        self.languages = languages

    def get_files_to_filter(self):
        files_to_filter = []
        if SastLanguages.JAVASCRIPT in self.languages:
            files_to_filter += self._get_js_files_to_filter()
        return files_to_filter

    def _get_js_files_to_filter(self):
        js_files_to_filter = []

        for path in self.source_codes:
            js_files = []
            ts_files = []
            tsconfig_files = []
            for (dirpath, _, filenames) in os.walk(path):
                if '/node_modules/' in dirpath:
                    continue
                for filename in filenames:
                    if filename.endswith('.ts'):
                        ts_files.append({'full_path': os.sep.join([dirpath, filename]), 'dir': dirpath, 'name': filename})
                    if filename.endswith('tsconfig.json'):
                        tsconfig_files.append({'full_path': os.sep.join([dirpath, filename]), 'dir': dirpath, 'name': filename})
                    if filename.endswith('.js'):
                        js_files.append({'full_path': os.sep.join([dirpath, filename]), 'dir': dirpath, 'name': filename})

            js_files_to_filter += FilesFilterManager._filter_by_tsconfig(tsconfig_files)
            js_files_to_filter += FilesFilterManager._filter_direct_build_js(tsconfig_files, js_files, ts_files, js_files_to_filter)

        return js_files_to_filter

    @staticmethod
    def _filter_direct_build_js(tsconfig_files, js_files, ts_files, filtered_by_tsconfig):
        js_files_to_filter = []
        for js_file in js_files:
            js_dir = js_file.get('dir')

        return js_files_to_filter



    @staticmethod
    def _filter_by_tsconfig(tsconfig_files):
        js_files_to_filter = []
        for tsconfig_file in tsconfig_files:
            with open(tsconfig_file.get('full_path')) as fp:
                config = json.load(fp)
            out_dir = config.get('compilerOptions', {}).get('outDir')
            out_file = config.get('compilerOptions', {}).get('outFile')
            if out_dir:
                build_dir = out_dir
            elif out_file:
                build_dir = out_file
            else: 
                continue

            # relative path
            if not build_dir.startswith('/'):
                build_path = os.path.abspath(tsconfig_file.get('dir') + '/' + build_dir)
            # absolute path
            else:
                build_path = build_dir
            js_files_to_filter.append(build_path)
        return js_files_to_filter