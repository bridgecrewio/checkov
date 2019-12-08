import logging

# set up logging to file - see previous section for more details
from checkov.terraform.parser import Parser
from checkov.terraform.checks.resource.registry import resource_registry

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)

if __name__ == '__main__':
    tf_defenitions = {}
    root_folder = "/Users/tronxd/WebstormProjects/platform/src/stacks/baseStack"
    Parser().hcl2(directory=root_folder, tf_defenitions=tf_defenitions)
    for definition in tf_defenitions.items():
        scanned_file = definition[0].split(root_folder)[1]
        logging.debug("Scanning file: %s", scanned_file)
        if 'resource' in definition[1]:
            for resource in definition[1]['resource']:
                resource_registry.run(resource, scanned_file)
