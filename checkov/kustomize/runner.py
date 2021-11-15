import io
import logging
import operator
import os
import shutil
import subprocess  # nosec
import tempfile
from functools import reduce

import yaml
import pathlib
import glob

from checkov.common.output.report import Report
#from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.kubernetes.registry import registry
from checkov.kubernetes.runner import Runner, _parse_files, K8_POSSIBLE_ENDINGS, _is_invalid_k8_definition 
from checkov.runner_filter import RunnerFilter
from checkov.common.util.data_structures_utils import search_deep_keys
from checkov.common.util.type_forcers import force_list
from checkov.common.output.record import Record

class K8sKustomizeRunner(Runner):

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True, helmChart=None):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        if files:
            _parse_files(files, definitions, definitions_raw)

        if root_folder:
            filepath_fn = lambda f: f'/{os.path.relpath(f, os.path.commonprefix((root_folder, f)))}'
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)

                for file in f_names:
                    file_ending = os.path.splitext(file)[1]
                    if file_ending in K8_POSSIBLE_ENDINGS:
                        full_path = os.path.join(root, file)
                        if "/." not in full_path and file not in ['package.json','package-lock.json']:
                            # skip temp directories
                            files_list.append(full_path)

            _parse_files(files_list, definitions, definitions_raw, filepath_fn)

        for k8_file in definitions.keys():

            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which sls_file does not always give).
            if k8_file[0] == '/':
                path_to_convert = (root_folder + k8_file) if root_folder else k8_file
            else:
                path_to_convert = (os.path.join(root_folder, k8_file)) if root_folder else k8_file

            file_abs_path = os.path.abspath(path_to_convert)

            if definitions[k8_file]:
                for i in range(len(definitions[k8_file])):
                    if (not 'apiVersion' in definitions[k8_file][i].keys()) and (not 'kind' in definitions[k8_file][i].keys()):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]
                    if entity_conf is None:
                        continue

                    # Split out resources if entity kind is List
                    if isinstance(entity_conf, dict) and entity_conf["kind"] == "List":
                        for item in entity_conf.get("items", []):
                            definitions[k8_file].append(item)

                for i in range(len(definitions[k8_file])):
                    if _is_invalid_k8_definition(definitions[k8_file][i]):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]

                    if isinstance(entity_conf, dict) and entity_conf.get("kind") == "List":
                        continue

                    # Skip entity without metadata["name"]
                    if isinstance(entity_conf, dict) and entity_conf.get("metadata"):
                        if isinstance(entity_conf["metadata"], int) or "name" not in entity_conf["metadata"]:
                            continue
                    else:
                        continue

                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if "ownerReferences" in entity_conf["metadata"] and \
                            entity_conf["metadata"]["ownerReferences"] is not None:
                        continue

                    # Append containers and initContainers to definitions list
                    for type in ["containers", "initContainers"]:
                        containers = []
                        if entity_conf["kind"] == "CustomResourceDefinition":
                            continue
                        containers = search_deep_keys(type, entity_conf, [])
                        if not containers:
                            continue
                        containers = containers.pop()
                        #containers.insert(0,entity_conf['kind'])
                        containerDef = {}
                        namespace = ""
                        if "namespace" in entity_conf["metadata"]:
                            namespace = entity_conf["metadata"]["namespace"]
                        else:
                            namespace = "default"
                        containerDef["containers"] = containers.pop()
                        if containerDef["containers"] is not None:
                            containerDef["containers"] = force_list(containerDef["containers"])
                            for cd in containerDef["containers"]:
                                i = containerDef["containers"].index(cd)
                                containerDef["containers"][i]["apiVersion"] = entity_conf["apiVersion"]
                                containerDef["containers"][i]["kind"] = type
                                containerDef["containers"][i]["parent"] = "{}.{}.{} (container {})".format(
                                    entity_conf["kind"], entity_conf["metadata"]["name"], namespace, str(i))
                                containerDef["containers"][i]["parent_metadata"] = entity_conf["metadata"]
                            definitions[k8_file].extend(containerDef["containers"])

                # Run for each definition included added container definitions
                for i in range(len(definitions[k8_file])):
                    if _is_invalid_k8_definition(definitions[k8_file][i]):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, definitions[k8_file][i], indent=2))

                    entity_conf = definitions[k8_file][i]
                    if entity_conf is None:
                        continue
                    if isinstance(entity_conf, dict) and (entity_conf["kind"] == "List" or not entity_conf.get("kind")):
                        continue

                    if isinstance(entity_conf, dict) and isinstance(entity_conf.get("kind"), int):
                        continue
                    # Skip entity without metadata["name"] or parent_metadata["name"]
                    if not any(x in entity_conf["kind"] for x in ["containers", "initContainers"]):
                        if entity_conf.get("metadata"):
                            if isinstance(entity_conf["metadata"], int) or not "name" in entity_conf["metadata"]:
                                continue
                        else:
                            continue

                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if "metadata" in entity_conf:
                        if "ownerReferences" in entity_conf["metadata"] and \
                                entity_conf["metadata"]["ownerReferences"] is not None:
                            continue

                    # Skip Kustomization Templates (for now)
                    if entity_conf["kind"] == "Kustomization":
                        continue

                    skipped_checks = get_skipped_checks(entity_conf)

                    results = registry.scan(k8_file, entity_conf, skipped_checks, runner_filter)

                    start_line = entity_conf["__startline__"]
                    end_line = entity_conf["__endline__"]

                    if start_line == end_line:
                        entity_lines_range = [start_line, end_line]
                        entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line]
                    else:
                        entity_lines_range = [start_line, end_line - 1]
                        entity_code_lines = definitions_raw[k8_file][start_line - 1: end_line - 1]

                    # TODO? - Variable Eval Message!
                    variable_evaluations = {}

                    for check, check_result in results.items():
                        resource_id = check.get_resource_id(entity_conf)
                        report.add_resource(f'{k8_file}:{resource_id}')
                        record = Record(check_id=check.id, bc_check_id=check.bc_id,
                                        check_name=check.name, check_result=check_result,
                                        code_block=entity_code_lines, file_path=k8_file,
                                        file_line_range=entity_lines_range,
                                        resource=resource_id, evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__, file_abs_path=file_abs_path)
                        record.set_guideline(check.guideline)
                        report.add_record(record=record)

        return report


class Runner(BaseRunner):
    check_type = "kustomize"
    kustomize_command = 'kustomize'
    system_deps = True
    potentialBases = []
    potentialOverlays = []

    @staticmethod
    def findKustomizeDirectories(root_folder, files, excluded_paths):
        kustomizeDirectories = []
        if not excluded_paths:
            excluded_paths = []
        if files:
            logging.info('Running with --file argument; file must be a kustomization.yaml file')
            for file in files:
                if os.path.basename(file) == 'kustomization.yaml':
                    kustomizeDirectories.append(os.path.dirname(file))

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, excluded_paths)
                filter_ignored_paths(root, f_names, excluded_paths)
                if 'kustomization.yaml' in f_names:
                    kustomizeDirectories.append(root)

        return kustomizeDirectories

    @staticmethod
    def parseKustomization(parseKustomizationData):
        # We may have multiple results for "kustomization.yaml" files. These could be:
        ## - Base and Environment (overlay) DIR's for the same kustomize-powered deployment
        ## - OR, Multiple different Kustomize-powered deployments
        ## - OR, a mixture of the two.
        ## We need parse some of the Kustomization.yaml files to work out which
        ## This is so we can provide "Environment" information back to the user as part of the checked resource name/description.
        ## TODO: We could also add a --kustomize-environment option so we only scan certain overlay names (prod, test etc) useful in CI.
        with open(f"{parseKustomizationData}/kustomization.yaml", 'r') as kustomizationFile:
            metadata = {}
            try:
                fileContent = yaml.safe_load(kustomizationFile)
            except yaml.YAMLError as exc:
                logging.info(f"Failed to load Kustomize metadata from {parseKustomizationData}/kustomization.yaml. details: {exc}")
    
            if 'resources' in fileContent:
                logging.debug(f"Kustomization contains resources: section. Likley a base. {parseKustomizationData}/kustomization.yaml")
                metadata['type'] =  "base"

            elif 'patchesStrategicMerge' in fileContent:
                logging.debug(f"Kustomization contains patchesStrategicMerge: section. Likley an overlay/env. {parseKustomizationData}/kustomization.yaml")
                metadata['type'] =  "overlay"
                if 'bases' in fileContent:
                 metadata['referenced_bases'] = fileContent['bases']

            elif 'bases' in fileContent.get:
                logging.debug(f"Kustomization contains bases: section. Likley an overlay/env. {parseKustomizationData}/kustomization.yaml")
                metadata['type'] =  "overlay"
                metadata['referenced_bases'] = fileContent['bases']

            metadata['fileContent'] = fileContent
            metadata['filePath'] = f"{parseKustomizationData}/kustomization.yaml"
            if metadata['type'] == "base":
                Runner.potentialBases.append(metadata['filePath'])

            if metadata['type'] == "overlay":
                Runner.potentialOverlays.append(metadata['filePath'])
               
        return metadata

    def check_system_deps(self):
        # Ensure local system dependancies are available and of the correct version.
        # Returns framework names to skip if deps **fail** (ie, return None for a successful deps check).
        logging.info(f"Checking necessary system dependancies for {self.check_type} checks.")
        try:
            proc = subprocess.Popen([self.kustomize_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = proc.communicate()
            oString = str(o, 'utf-8')

            if "Version:" in oString:
                kustomizeVersionOutput = oString[oString.find('/') + 1: oString.find('G') - 1]
                logging.info(f"Found working version of {self.check_type} dependancies: {kustomizeVersionOutput}")
                return None
            else:
                return self.check_type
        except Exception:
            logging.info(f"Error running necessary tools to process {self.check_type} checks.")
            return self.check_type

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):

        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        #TODO, check if kubernetes external checks are correctly loaded when triggered from kustomize (and helm) frameworks, if not we need to load the k8s custom checks here calling the k8s registry class.
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        kustomizeDirectories = self.findKustomizeDirectories(root_folder, files, runner_filter.excluded_paths)

        report = Report(self.check_type)
        KustomizeProcessedFolderAndMeta = {}
        #KustomizeProcessedFolderAndMeta = parallel_runner.run_function(
        #    lambda parseKustomizationData: (parseKustomizationData, self.parseKustomization(parseKustomizationData)), kustomizeDirectories)
        for kustomizedir in kustomizeDirectories:
            KustomizeProcessedFolderAndMeta[kustomizedir] = self.parseKustomization(kustomizedir)
        
        with tempfile.TemporaryDirectory() as target_dir:
            for filePath in KustomizeProcessedFolderAndMeta:    
                # Name our Kustomize overlays/environments.
                ## We try to validate any existing base references in the yaml and also find our own "bases" if possible as absolute paths.
                ## The delta of paths between the closest base and an overlay dir will be used as the env name for a given kustomize overlay
                ## as they dont have "names" per-se, and we need a unique resource name for the checkov results.

                logging.debug(f"Kustomization at {filePath} likley a {KustomizeProcessedFolderAndMeta[filePath]['type']}")
                if KustomizeProcessedFolderAndMeta[filePath]['type'] == 'overlay':
                    for parent in pathlib.Path(filePath).parents:
                        for potentialBase in Runner.potentialBases:
                            pathlibBaseObject = pathlib.Path(potentialBase)
                            potentialBasePath = pathlibBaseObject.parents[1]
                            if parent == potentialBasePath.resolve():
                                KustomizeProcessedFolderAndMeta[filePath]['calculated_bases'] = str(pathlibBaseObject.parent)
                    # Normalize referenced bases vs calculated (referenced will usually be relative, calculated absolute)
                    ## TODO: If someone can show me an example where base: isnt relative:
                    ### if "../" in KustomizeProcessedFolderAndMeta[filePath]['referenced_bases']:
                    #### TODO: Validate if this breaks non POSIX windows paths, as everything else is handled by pathlib/os.paths
                    try: 
                        relativeToFullPath = f"{filePath}/{KustomizeProcessedFolderAndMeta[filePath]['referenced_bases'][0]}"


                        if pathlib.Path(KustomizeProcessedFolderAndMeta[filePath]['calculated_bases']) == pathlib.Path(relativeToFullPath).resolve():
                            KustomizeProcessedFolderAndMeta[filePath]['validated_base'] = str(pathlib.Path(KustomizeProcessedFolderAndMeta[filePath]['calculated_bases']))
                            checkovKustomizeEnvNameByPath = pathlib.Path(filePath).relative_to(pathlib.Path(KustomizeProcessedFolderAndMeta[filePath]['calculated_bases']).parent)
                            KustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                            logging.debug(f"Overlay based on {KustomizeProcessedFolderAndMeta[filePath]['validated_base']}, naming overlay {checkovKustomizeEnvNameByPath} for Checkov Results.")
                        else:
                            checkovKustomizeEnvNameByPath = f"UNVALIDATEDBASEDIR/{pathlib.Path(filePath).stem}"
                            KustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                            logging.warning(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")

                    except KeyError:
                        checkovKustomizeEnvNameByPath = f"UNVALIDATEDBASEDIR/{pathlib.Path(filePath).stem}"
                        KustomizeProcessedFolderAndMeta[filePath]['overlay_name'] = checkovKustomizeEnvNameByPath
                        logging.warning(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")
            
                # Template out the Kustomizations to Kubernetes YAML
                try:
                
                    proc = subprocess.Popen([self.kustomize_command, 'build', filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                    o, e = proc.communicate()
                    logging.info(
                        f"Ran {self.kustomize_command} command to build Kustomize output. DIR: {filePath}. TYPE: {KustomizeProcessedFolderAndMeta[filePath]['type']}.")

                except Exception:
                    logging.warning(
                        f"Error build Kustomize output at dir: {filePath}. Error details: {str(e, 'utf-8')}")
                    continue

                if KustomizeProcessedFolderAndMeta[filePath]['type'] == "overlay":
                    basePathParents = pathlib.Path(KustomizeProcessedFolderAndMeta[filePath]['calculated_bases']).parents
                    mostSignificantBasePath = "/" + basePathParents._parts[-3] + "/" + basePathParents._parts[-2] + "/" + basePathParents._parts[-1]
                    envOrBasePathPrefix = mostSignificantBasePath + "/" + str(KustomizeProcessedFolderAndMeta[filePath]['overlay_name'])

                if KustomizeProcessedFolderAndMeta[filePath]['type'] == "base":
                    # Validated base last three parents as a path
                    basePathParents = pathlib.Path(KustomizeProcessedFolderAndMeta[filePath]['filePath']).parents
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

                #HACK Helm/k8s page-to-file parser works well, but we expect the file to start with ---.
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

                        if not s.startswith('apiVersion:'):
                            raise Exception(f'Line {line_num}: Expected line to start with apiVersion:  {s}')
                        #TODO: GET SOURCE FROM LATER ON AND RENAME PLACEHOLDER
                        source = file_num
                        file_num += 1 
                        if source != cur_source_file:
                            if cur_writer:
                                cur_writer.close()
                            file_path = os.path.join(extractDir, str(source))
                            parent = os.path.dirname(file_path)
                            os.makedirs(parent, exist_ok=True)
                            cur_source_file = source
                            cur_writer = open(os.path.join(extractDir, str(source)), 'a')
                        cur_writer.write('---' + os.linesep)
                        cur_writer.write(s + os.linesep)

                        last_line_dashes = False
                    
                    else:

                        if s.startswith('apiVersion:'):
                            raise Exception(f'Line {line_num}: Unexpected line starting with apiVersion:  {s}')

                        if not cur_writer:
                            continue
                        else:
                            cur_writer.write(s + os.linesep)

                    line_num += 1

                if cur_writer:
                    cur_writer.close()

            # Now we have all our K8S templates in seperate placeholder files by number from the Kustomize build blob. 
            # Rename them to useful information from the K8S metadata before continuing.
            for file in glob.iglob(f"{target_dir}/**", recursive=True):
                try:
                    with open(file) as f:
                        currentYamlObject = yaml.safe_load(f)
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
                        os.rename(file, str(pathlib.Path(file).parent) + "/" + filename) 
                except IsADirectoryError:
                    continue
            try:
                if KustomizeProcessedFolderAndMeta[filePath]['type'] == 'overlay':
                    identityToK8sScanner = str(KustomizeProcessedFolderAndMeta[filePath]['overlay_name'])
                if KustomizeProcessedFolderAndMeta[filePath]['type'] == 'base':
                    identityToK8sScanner = "base"
                k8s_runner = K8sKustomizeRunner()
                chart_results = k8s_runner.run(target_dir, external_checks_dir=external_checks_dir,
                                                runner_filter=runner_filter, helmChart=identityToK8sScanner)
                logging.debug(f"Sucessfully ran k8s scan on {identityToK8sScanner}. Scan dir : {target_dir}")
                report.failed_checks += chart_results.failed_checks
                report.passed_checks += chart_results.passed_checks
                report.parsing_errors += chart_results.parsing_errors
                report.skipped_checks += chart_results.skipped_checks
                report.resources.update(chart_results.resources)

            except Exception as e:
                logging.warning(e, stack_info=True)
                with tempfile.TemporaryDirectory() as save_error_dir:
                    logging.debug(
                        f"Error running k8s scan on {identityToK8sScanner}. Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
                    shutil.move(target_dir, save_error_dir)

        return report


def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    if not isinstance(entity_conf, dict):
        return skipped
    if entity_conf["kind"] == "containers" or entity_conf["kind"] == "initContainers":
        metadata = entity_conf["parent_metadata"]
    else:
        if "metadata" in entity_conf.keys():
            metadata = entity_conf["metadata"]
    if "annotations" in metadata.keys() and metadata["annotations"] is not None:
        for key in metadata["annotations"].keys():
            skipped_item = {}
            if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                if "CKV_K8S" in metadata["annotations"][key]:
                    if "=" in metadata["annotations"][key]:
                        (skipped_item["id"], skipped_item["suppress_comment"]) = metadata["annotations"][key].split("=")
                    else:
                        skipped_item["id"] = metadata["annotations"][key]
                        skipped_item["suppress_comment"] = "No comment provided"
                    skipped.append(skipped_item)
                else:
                    logging.info(
                        "Parse of Annotation Failed for {}: {}".format(metadata["annotations"][key], entity_conf,
                                                                       indent=2))
                    continue
    return skipped


def _get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def find_lines(node, kv):
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        for i in node:
            for x in find_lines(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_lines(j, kv):
                yield x
