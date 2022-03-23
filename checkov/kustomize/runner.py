import io
import logging
import os
import pathlib
import shutil
import subprocess  # nosec
import tempfile

import yaml

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.kubernetes.kubernetes_utils import get_resource_id
from checkov.kubernetes.runner import Runner as K8sRunner
from checkov.kubernetes.runner import _get_entity_abs_path
from checkov.runner_filter import RunnerFilter


class K8sKustomizeRunner(K8sRunner):

    def mutateKubernetesResults(self, results, report, k8_file=None, k8_file_path=None, file_abs_path=None, entity_conf=None, variable_evaluations=None, reportMutatorData=None):
        # Moves report generation logic out of checkov.kubernetes.runner.run() def.
        # Allows us to overriding report file information for "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        kustomizeMetadata = reportMutatorData['kustomizeMetadata'], 
        kustomizeFileMappings = reportMutatorData['kustomizeFileMappings']
        for check, check_result in results.items():
            resource_id = get_resource_id(entity_conf)
            entity_context = self.context[k8_file][resource_id]
            
            if file_abs_path in kustomizeFileMappings:
                realKustomizeEnvMetadata = kustomizeMetadata[0][kustomizeFileMappings[file_abs_path]]
                if 'overlay' in realKustomizeEnvMetadata["type"]:
                    kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{resource_id}'
                else:
                    kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{resource_id}'
            else: 
                kustomizeResourceID = "Unknown error. This is a bug."

            code_lines = entity_context.get("code_lines")
            file_line_range = self.line_range(code_lines)
            record = Record(
                check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                check_result=check_result, code_block=code_lines, file_path=realKustomizeEnvMetadata['filePath'],
                file_line_range=file_line_range,
                resource=kustomizeResourceID, evaluations=variable_evaluations,
                check_class=check.__class__.__module__, file_abs_path=realKustomizeEnvMetadata['filePath'], severity=check.severity)
            record.set_guideline(check.guideline)
            report.add_record(record=record)
        
        return report

    def line_range(self, code_lines):
        num_of_lines = len(code_lines)
        file_line_range = [0, 0]
        if num_of_lines > 0:
            first_line, code = code_lines[0]
            last_line, code = code_lines[num_of_lines - 1]
            file_line_range = [first_line, last_line]
        return file_line_range

    def mutateKubernetesGraphResults(self, root_folder: str, runner_filter: RunnerFilter, report: Report, checks_results, reportMutatorData=None) -> Report:
        # Moves report generation logic out of run() method in Runner class.
        # Allows function overriding of a much smaller function than run() for other "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        kustomizeMetadata = reportMutatorData['kustomizeMetadata'], 
        kustomizeFileMappings = reportMutatorData['kustomizeFileMappings']

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path = entity.get(CustomAttributes.FILE_PATH)
                entity_file_abs_path = _get_entity_abs_path(root_folder, entity_file_path)
                entity_id = entity.get(CustomAttributes.ID)
                entity_context = self.context[entity_file_path][entity_id]

                if entity_file_abs_path in kustomizeFileMappings:
                    realKustomizeEnvMetadata = kustomizeMetadata[0][kustomizeFileMappings[entity_file_abs_path]]
                    if 'overlay' in realKustomizeEnvMetadata["type"]:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{entity_id}'
                    else:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{entity_id}'
                else: 
                    kustomizeResourceID = "Unknown error. This is a bug."
                code_lines = entity_context.get("code_lines")
                file_line_range = self.line_range(code_lines)

                record = Record(
                    check_id=check.id,
                    check_name=check.name,
                    check_result=check_result,
                    code_block=entity_context.get("code_lines"),
                    file_path=realKustomizeEnvMetadata['filePath'],
                    file_line_range=file_line_range,
                    resource=kustomizeResourceID,  # entity.get(CustomAttributes.ID),
                    evaluations={},
                    check_class=check.__class__.__module__,
                    file_abs_path=entity_file_abs_path,
                    severity=check.severity
                )
                record.set_guideline(check.guideline)
                report.add_record(record=record)

        return report

class Runner(BaseRunner):
    kustomize_command = 'kustomize'
    kubectl_command = 'kubectl'
    check_type = CheckType.KUSTOMIZE
    system_deps = True
    potentialBases = []
    potentialOverlays = []
    kustomizeProcessedFolderAndMeta = {}
    kustomizeFileMappings = {}
    kustomizeSupportedFileTypes = ('kustomization.yaml', 'kustomization.yml')
    templateRendererCommand = None

    @staticmethod
    def findKustomizeDirectories(root_folder, files, excluded_paths):
        kustomizeDirectories = []
        if not excluded_paths:
            excluded_paths = []
        if files:
            logging.info('Running with --file argument; file must be a kustomization.yaml file')
            for file in files:
                if os.path.basename(file) in Runner.kustomizeSupportedFileTypes:
                    kustomizeDirectories.append(os.path.dirname(file))

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, excluded_paths)
                filter_ignored_paths(root, f_names, excluded_paths)
                [kustomizeDirectories.append(os.path.abspath(root)) for x in f_names if x in Runner.kustomizeSupportedFileTypes]

        return kustomizeDirectories

    @staticmethod
    def parseKustomization(parseKustomizationData):
        # We may have multiple results for "kustomization.yaml" files. These could be:
        # - Base and Environment (overlay) DIR's for the same kustomize-powered deployment
        # - OR, Multiple different Kustomize-powered deployments
        # - OR, a mixture of the two.
        # We need parse some of the Kustomization.yaml files to work out which
        # This is so we can provide "Environment" information back to the user as part of the checked resource name/description.
        # TODO: We could also add a --kustomize-environment option so we only scan certain overlay names (prod, test etc) useful in CI.
        yaml_path = os.path.join(parseKustomizationData,"kustomization.yaml")
        yml_path = os.path.join(parseKustomizationData,"kustomization.yml")
        if os.path.isfile(yml_path):
            kustomization_path = yml_path
        elif os.path.isfile(yaml_path):
            kustomization_path = yaml_path
        else:
            return {}


        with open(kustomization_path, 'r') as kustomizationFile:
            metadata = {}
            try:
                fileContent = yaml.safe_load(kustomizationFile)
            except yaml.YAMLError:
                logging.info(f"Failed to load Kustomize metadata from {kustomization_path}.", exc_info=True)
    
            if 'resources' in fileContent:
                logging.debug(f"Kustomization contains resources: section. Likley a base. {kustomization_path}")
                metadata['type'] = "base"

            elif 'patchesStrategicMerge' in fileContent:
                logging.debug(f"Kustomization contains patchesStrategicMerge: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                if 'bases' in fileContent:
                    metadata['referenced_bases'] = fileContent['bases']

            elif 'bases' in fileContent:
                logging.debug(f"Kustomization contains bases: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                metadata['referenced_bases'] = fileContent['bases']

            metadata['fileContent'] = fileContent
            metadata['filePath'] = f"{kustomization_path}"
            if metadata['type'] == "base":
                Runner.potentialBases.append(metadata['filePath'])

            if metadata['type'] == "overlay":
                Runner.potentialOverlays.append(metadata['filePath'])
               
        return metadata

    def check_system_deps(self):
        # Ensure local system dependancies are available and of the correct version.
        # Returns framework names to skip if deps **fail** (ie, return None for a successful deps check).
        logging.info(f"Checking necessary system dependancies for {self.check_type} checks.")

        if shutil.which(self.kubectl_command) is not None:
            try:
                proc = subprocess.Popen([self.kubectl_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                o, e = proc.communicate()
                oString = str(o, 'utf-8')

                if "Client Version:" in oString:
                    kubectlVersionMajor = oString.split('\n')[0].split('Major:\"')[1].split('"')[0]
                    kubectlVersionMinor = oString.split('\n')[0].split('Minor:\"')[1].split('"')[0]
                    kubectlVersion = float(f"{kubectlVersionMajor}.{kubectlVersionMinor}")
                    if kubectlVersion >= 1.14:
                        logging.info(f"Found working version of {self.check_type} dependancy {self.kubectl_command}: {kubectlVersion}")
                        self.templateRendererCommand = self.kubectl_command
                        return None
            
            except Exception:
                logging.debug(f"An error occured testing the {self.kubectl_command} command: {e}")
                pass

        elif shutil.which(self.kustomize_command) is not None:
    
            try:
                proc = subprocess.Popen([self.kustomize_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                o, e = proc.communicate()
                oString = str(o, 'utf-8')

                if "Version:" in oString:
                    kustomizeVersionOutput = oString[oString.find('/') + 1: oString.find('G') - 1]
                    logging.info(f"Found working version of {self.check_type} dependancy {self.kustomize_command}: {kustomizeVersionOutput}")
                    self.templateRendererCommand = self.kustomize_command
                    return None
                else:
                    return self.check_type

            except Exception:
                logging.debug(f"An error occured testing the {self.kustomize_command} command: {e}")
                pass
        
        else:
            logging.info(f"Could not find usable tools locally to process {self.check_type} checks. Framework will be disabled for this run.")
            return self.check_type

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):

        kustomizeDirectories = self.findKustomizeDirectories(root_folder, files, runner_filter.excluded_paths)

        report = Report(self.check_type)
        for kustomizedir in kustomizeDirectories:
            self.kustomizeProcessedFolderAndMeta[kustomizedir] = self.parseKustomization(kustomizedir)
        
        with tempfile.TemporaryDirectory() as target_dir:
            for filePath in self.kustomizeProcessedFolderAndMeta:    
                # Name our Kustomize overlays/environments.
                # We try to validate any existing base references in the yaml and also find our own "bases" if possible as absolute paths.
                # The delta of paths between the closest base and an overlay dir will be used as the env name for a given kustomize overlay
                # as they dont have "names" per-se, and we need a unique resource name for the checkov results.

                logging.debug(f"Kustomization at {filePath} likley a {self.kustomizeProcessedFolderAndMeta[filePath]['type']}")
                if self.kustomizeProcessedFolderAndMeta[filePath]['type'] == 'overlay':
                    for parent in pathlib.Path(filePath).parents:
                        for potentialBase in Runner.potentialBases:
                            pathlibBaseObject = pathlib.Path(potentialBase)
                            potentialBasePath = pathlibBaseObject.parents[1]
                            if parent == potentialBasePath.resolve():
                                self.kustomizeProcessedFolderAndMeta[filePath]['calculated_bases'] = str(pathlibBaseObject.parent)
                    # Normalize referenced bases vs calculated (referenced will usually be relative, calculated absolute)
                    # TODO: If someone can show me an example where base: isnt relative:
                    # if "../" in self.kustomizeProcessedFolderAndMeta[filePath]['referenced_bases']:
                    # TODO: Validate if this breaks non POSIX windows paths, as everything else is handled by pathlib/os.paths
                    try: 
                        relativeToFullPath = f"{filePath}/{self.kustomizeProcessedFolderAndMeta[filePath]['referenced_bases'][0]}"


                        if pathlib.Path(self.kustomizeProcessedFolderAndMeta[filePath]['calculated_bases']) == pathlib.Path(relativeToFullPath).resolve():
                            self.kustomizeProcessedFolderAndMeta[filePath]['validated_base'] = str(pathlib.Path(self.kustomizeProcessedFolderAndMeta[filePath]['calculated_bases']))
                            checkovKustomizeEnvNameByPath = pathlib.Path(filePath).relative_to(pathlib.Path(self.kustomizeProcessedFolderAndMeta[filePath]['calculated_bases']).parent)
                            self.kustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                            logging.debug(f"Overlay based on {self.kustomizeProcessedFolderAndMeta[filePath]['validated_base']}, naming overlay {checkovKustomizeEnvNameByPath} for Checkov Results.")
                        else:
                            checkovKustomizeEnvNameByPath = f"{pathlib.Path(filePath).stem}"
                            self.kustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                            logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")

                    except KeyError:
                        checkovKustomizeEnvNameByPath = f"{pathlib.Path(filePath).stem}"
                        self.kustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                        logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")
            

                if self.templateRendererCommand == "kubectl":
                    templateRenderCommandOptions = "kustomize"
                if self.templateRendererCommand == "kustomize":
                    templateRenderCommandOptions = "build"
                    
                # Template out the Kustomizations to Kubernetes YAML
                try:
                    proc = subprocess.Popen([self.templateRendererCommand, templateRenderCommandOptions, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                    o, e = proc.communicate()
                    logging.info(
                        f"Ran {self.templateRendererCommand} to build Kustomize output. DIR: {filePath}. TYPE: {self.kustomizeProcessedFolderAndMeta[filePath]['type']}.")

                except Exception:
                    logging.warning(f"Error building Kustomize output at dir: {filePath}.", exc_info=True)
                    continue

                if self.kustomizeProcessedFolderAndMeta[filePath]['type'] == "overlay":
                    if 'calculated_bases' not in self.kustomizeProcessedFolderAndMeta[filePath]:
                        logging.debug(f"Kustomize: Overlay with unknown base. User may have specified overlay dir directly. {filePath}")
                        envOrBasePathPrefix = ""
                    else:
                        basePathParents = pathlib.Path(self.kustomizeProcessedFolderAndMeta[filePath]['calculated_bases']).parents
                        mostSignificantBasePath = "/" + basePathParents._parts[-3] + "/" + basePathParents._parts[-2] + "/" + basePathParents._parts[-1]
                        envOrBasePathPrefix = f"{mostSignificantBasePath}/{self.kustomizeProcessedFolderAndMeta[filePath]['overlay_name']}"

                if self.kustomizeProcessedFolderAndMeta[filePath]['type'] == "base":
                    # Validated base last three parents as a path
                    basePathParents = pathlib.Path(self.kustomizeProcessedFolderAndMeta[filePath]['filePath']).parents
                    mostSignificantBasePath = "/" + basePathParents._parts[-4] + "/" + basePathParents._parts[-3] + "/" + basePathParents._parts[-2]
                    envOrBasePathPrefix = mostSignificantBasePath

                extractDir = target_dir + envOrBasePathPrefix
                os.makedirs(extractDir, exist_ok=True)

                logging.debug(f"Kustomize: Temporary directory for {filePath} at {extractDir}")
                output = str(o, 'utf-8')
                cur_source_file = None
                cur_writer = None
                last_line_dashes = False
                line_num = 1
                file_num = 0

                # page-to-file parser from helm framework works well, but we expect the file to start with --- in this case from Kustomize.
                output = "---\n" + output
                reader = io.StringIO(output)
                
                for s in reader:
                    s = s.rstrip()

                    if s == '---':
                        last_line_dashes = True
                        continue

                    if last_line_dashes:
                        # The next line should contain a "apiVersion" line for the next Kubernetes manifest
                        # So we will close the old file, open a new file, and write the dashes from last iteration plus this line
                        source = file_num
                        file_num += 1 
                        if source != cur_source_file:
                            if cur_writer:
                                # Here we are about to close a "complete" file. The function will validate it looks like a K8S manifest before continuing.
                                self._curWriterValidateStoreMapAndClose(cur_writer, filePath)
                                # 
                            file_path = os.path.join(extractDir, str(source))
                            parent = os.path.dirname(file_path)
                            os.makedirs(parent, exist_ok=True)
                            cur_source_file = source
                            cur_writer = open(os.path.join(extractDir, str(source)), 'a')
                        cur_writer.write('---' + os.linesep)
                        cur_writer.write(s + os.linesep)

                        last_line_dashes = False
                    
                    else:
                        
                        if not cur_writer:
                            continue
                        else:
                            cur_writer.write(s + os.linesep)

                    line_num += 1

                if cur_writer:
                    self._curWriterValidateStoreMapAndClose(cur_writer, filePath)

            try:
                k8s_runner = K8sKustomizeRunner()
                reportMutatorData = {'kustomizeMetadata':self.kustomizeProcessedFolderAndMeta,'kustomizeFileMappings':self.kustomizeFileMappings}
                # k8s_runner.run() will kick off both CKV_ and CKV2_ checks and return a merged results object.
                chart_results = k8s_runner.run(target_dir, external_checks_dir=None,
                                                runner_filter=runner_filter, reportMutatorData=reportMutatorData)
                logging.debug(f"Sucessfully ran k8s scan on Kustomization templated files in tmp scan dir : {target_dir}")
                report.failed_checks += chart_results.failed_checks
                report.passed_checks += chart_results.passed_checks
                report.parsing_errors += chart_results.parsing_errors
                report.skipped_checks += chart_results.skipped_checks
                report.resources.update(chart_results.resources)

            except Exception:
                logging.warning("Failed to run Kubernetes runner", exc_info=True)
                with tempfile.TemporaryDirectory() as save_error_dir:
                    logging.debug(
                        f"Error running k8s scan on Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
                    shutil.move(target_dir, save_error_dir)

        return report

    def _curWriterValidateStoreMapAndClose(self, cur_writer, FilePath):
        currentFileName = cur_writer.name
        cur_writer.close()
        # Now we have a complete k8s manifest as we closed the writer, and it's temporary file name (currentFileName) plus the original file templated out (FilePath)
        # Rename them to useful information from the K8S metadata before conting.
        # Then keep a mapping of template files to original kustomize repo locations for use with Checkov output later.
        try:
            with open(currentFileName) as f:
                currentYamlObject = yaml.safe_load(f)
                # Validate we have a K8S manifest
                if "apiVersion" in currentYamlObject:
                    itemName = []
                    itemName.append(currentYamlObject['kind'])
                    if 'namespace' in currentYamlObject['metadata']:
                        itemName.append(currentYamlObject['metadata']['namespace'])
                    else:
                        itemName.append("default")
                    if 'name' in currentYamlObject['metadata']:
                        itemName.append(currentYamlObject['metadata']['name'])
                    else:
                        itemName.append("noname")
            
                    filename = f"{'-'.join(itemName)}.yaml"
                    newFullPathFilename = str(pathlib.Path(currentFileName).parent / filename) 
                    os.rename(currentFileName, newFullPathFilename) 
                    self.kustomizeFileMappings[newFullPathFilename] = FilePath
                
                else:
                    raise Exception(f'Not a valid Kubernetes manifest (no apiVersion) while parsing Kustomize template: {FilePath}. Templated output: {currentFileName}.')

        except IsADirectoryError:
            pass
