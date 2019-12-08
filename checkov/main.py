import logging

# set up logging to file - see previous section for more details
from checkov.terraform.runner import Runner

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)

if __name__ == '__main__':
    root_folder = "/Users/barak/Documents/dev/platform2/src/stacks/baseStack"
    Runner().run(root_folder)
