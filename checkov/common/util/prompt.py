from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.util.banner import banner as checkov_banner
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2 import Template
import click
import jinja2
import os
import yaml
import importlib

CHECKOV_ROOT_DIRECTORY = os.path.join(".", "checkov")
TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), "templates")


class Prompt():
    ACTIONS = ["add"]
    CHECK_CLASS = ["terraform"]
    CATEGORIES = ["application_security", "backup_and_recovery" "convention", "encryption",
                  "general_security", "iam", "kubernetes", "logging", "networking", "secrets"]
    TERRAFORM_OBJECT_TYPE = ["data", "provider", "resource"]
    PROVIDERS = ["azure", "aws", "gcp"]

    PROMPTS = {
        "chosen_action": {
            "text": 'What action would you like to take?',
            "type": click.Choice(ACTIONS),
            "default": "add",
            "sub_prompts": [
                {
                    "title": {
                        "text": 'Enter the title of your new check (without a .py)',
                        "type": str,
                        "default": "MyNewTest"
                    },
                    "category": {
                        "text": 'Select a category for this check',
                        "type": click.Choice(CATEGORIES),
                        "default": "iam"
                    },
                    "desc": {
                        "text": 'Describe what this check does',
                        "type": str,
                        "default": "Ensure that X does Y..."
                    },
                    "check_class": {
                        "prompt_if": 'add',
                        "text": 'What kind of check would you like to add?',
                        "type": click.Choice(CHECK_CLASS),
                        "default": "terraform",
                        "sub_prompts": [
                            {  # Terraform
                                "provider": {
                                    "prompt_if": 'terraform',
                                    "text": 'Select the cloud provider this will run on',
                                    "type": click.Choice(PROVIDERS),
                                    "default": "aws",
                                    "sub_prompts": [
                                        {  # AWS
                                            "context": {
                                                "prompt_if": 'aws',
                                                "text": 'Select a terraform object for this check',
                                                "type": click.Choice(TERRAFORM_OBJECT_TYPE),
                                                "default": "resource",
                                                "sub_prompts": [
                                                    {
                                                        "supported_resource": {
                                                            "prompt_if": 'resource',
                                                            "text": 'Enter the terraform object type',
                                                            "type": str,
                                                            "default": "aws_iam_policy"
                                                        },
                                                    },
                                                    {
                                                        "supported_resource": {
                                                            "prompt_if": 'data',
                                                            "text": 'Enter the terraform object type',
                                                            "type": str,
                                                            "default": "aws_iam_policy_document"
                                                        },
                                                    },
                                                    {
                                                        "supported_resource": {
                                                            "prompt_if": 'provider',
                                                            "text": 'Enter the terraform object type',
                                                            "type": str,
                                                            "default": "aws"
                                                        },
                                                    }
                                                ]
                                            }
                                        },
                                        {  # Azure
                                            "context": {
                                                "prompt_if": 'azure',
                                                "text": 'Select a terraform object for this check',
                                                "type": click.Choice(['resource']),
                                                "default": "resource",
                                                "sub_prompts": [
                                                    {
                                                        "supported_resource": {
                                                            "prompt_if": 'resource',
                                                            "text": 'Enter the terraform object type',
                                                            "type": str,
                                                            "default": "azurerm_policy_definition"
                                                        },
                                                    }
                                                ]
                                            }
                                        },
                                        {  # GCP
                                            "context": {
                                                "prompt_if": 'gcp',
                                                "text": 'Select a terraform object for this check',
                                                "type": click.Choice(['resource']),
                                                "default": "resource",
                                                "sub_prompts": [
                                                    {
                                                        "supported_resource": {
                                                            "prompt_if": 'resource',
                                                            "text": 'Enter the terraform object type',
                                                            "type": str,
                                                            "default": "google_project_iam_policy"
                                                        },
                                                    }
                                                ]
                                            }
                                        },
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    def __init__(self):
        print(checkov_banner)
        self.responses = {}
        self.prompt()

    # Recurse over our prompt, populating new class attributes from the keys and
    # user-supplied answers
    def prompt(self, prompt_map=PROMPTS, prompt_if=None):
        for k, v in prompt_map.items():
            if "prompt_if" not in v or v["prompt_if"] == prompt_if:
                # Prompt the user
                p = click.prompt(v["text"], type=v["type"], default=v["default"])

                # Create the action on our object
                if k == 'chosen_action':
                    self.chosen_action = p

                # Record user responses
                self.responses[k] = p
                print()  # Newline for readability

                # Call prompt() again on any sub_prompts
                if "sub_prompts" in v:
                    for sub_prompt in v["sub_prompts"]:
                        self.prompt(sub_prompt, prompt_if=p)

    def template_env(self):
        template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIRECTORY)
        return jinja2.Environment(loader=template_loader, autoescape=True)


class Check(Prompt):
    def __init__(self, user_responses={}):
        self.chosen_action = user_responses.get("chosen_action", None)
        self.title = user_responses.get("title", None)
        self.category = user_responses.get("category", None)
        self.desc = user_responses.get("desc", None)
        self.check_class = user_responses.get("check_class", None)
        self.provider = user_responses.get("provider", None)
        self.context = user_responses.get("context", None)
        self.supported_resource = user_responses.get("supported_resource", None)

    def action(self):
        # Call the user-selected action (add, remove, modify - leaves room for more actions)
        getattr(self, self.chosen_action)()

    def add(self):
        print("Please ensure you are at the root of the Checkov repository before completing this prompt")

        self.populate_templates()
        self.create_check()
        self.create_unit_test_stubs()
        self.print_instructions()

    def populate_templates(self):
        # Fetch the tf template for unit tests
        tf_unit_test_template = self.template_env().get_template("unittest-terraform.jinja2")
        self.tf_unit_test_template = tf_unit_test_template.render(
            supported_resource=self.supported_resource, context=self.context)

        # Fetch the python template for unit tests
        python_unit_test_template = self.template_env().get_template("unittest-python.jinja2")
        self.python_unit_test_template = python_unit_test_template.render(
            provider=self.provider, title=self.title, supported_resource=self.supported_resource, check_class=self.check_class, context=self.context)

        # Fetch the init template
        init_template = self.template_env().get_template("init.jinja2")
        self.init_template = init_template.render()

        # Fetch the check template
        check_template = self.template_env().get_template(f"{self.context}.jinja2")
        new_index = self.get_latest_id_for_provider() + 1  # Find the latest ID and increment

        self.template = check_template.render(title=self.title, provider=self.provider.upper(),
                                              supported_resource=self.supported_resource, category=self.category.upper(),
                                              desc=self.desc, index=new_index)

    def get_latest_id_for_provider(self):
        max_id = 0
        try:
            for ck in BaseCheckRegistry.get_all_registered_checks():
                if ck.id.startswith(f"CKV_{self.provider.upper()}"):
                    curr_id_num = int(ck.id.split("_")[2])
                    if curr_id_num > max_id:
                        max_id = curr_id_num
        except Exception:
            print("Unable to automatically find latest Check ID, please set manually")
            max_id = 999999

        return max_id

    def create_check(self):
        # Create check in the checks directory
        ck_loc = os.path.abspath(os.path.join(CHECKOV_ROOT_DIRECTORY,
                                              self.check_class, "checks", self.context, self.provider.lower()))
        print(f"Creating Check {self.title}.py in {ck_loc}")

        # Set path, make directory path if necessary
        full_path = os.path.join(ck_loc, f"{self.title}.py")
        os.makedirs(ck_loc, exist_ok=True)

        # Write file
        with open(full_path, "w") as f:
            f.write(self.template)

        print(f"\tSuccessfully created {full_path}")

    def create_unit_test_stubs(self):
        base = os.path.abspath(os.path.join(CHECKOV_ROOT_DIRECTORY, os.path.pardir,
                                            "tests", self.check_class, "checks", self.context, self.provider.lower()))
        print(f"Creating Unit Test Stubs for {self.title} in {base}")

        # Create Terraform stub from Template
        new_dir = os.path.join(base, f"example_{self.title}")
        os.makedirs(new_dir, exist_ok=True)

        tf_loc = os.path.join(new_dir, f"{self.title}.tf")
        with open(tf_loc, "w") as f:
            f.write(self.tf_unit_test_template)

        print(f"\tSuccessfully created {tf_loc}")

        py_loc = os.path.join(base, f"test_{self.title}.py")

        with open(py_loc, "w") as f:
            f.write(self.python_unit_test_template)

        print(f"\tSuccessfully created {py_loc}")

    def print_instructions(self):
        print("\nNext steps:")
        print("\t1) Edit your new check located in the checks/ directory listed above")
        print("\t2) Add both a PASS and FAIL unit test to the newly created unit test under the tests/ directory to show others how to fix failures")
