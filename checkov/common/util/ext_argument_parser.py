from io import StringIO

import configargparse

from checkov.common.util.type_forcers import convert_str_to_bool


class ExtArgumentParser(configargparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields_to_sanitize = set()

    def add(self, *args, **kwargs):
        if kwargs.pop('sanitize', False):
            self.fields_to_sanitize.add(args[0])
        super().add(*args, **kwargs)

    def format_values(self, sanitize: bool = False) -> str:
        if not sanitize:
            return super().format_values()

        source_key_to_display_value_map = {
            configargparse._COMMAND_LINE_SOURCE_KEY: "Command Line Args: ",
            configargparse._ENV_VAR_SOURCE_KEY: "Environment Variables:\n",
            configargparse._CONFIG_FILE_SOURCE_KEY: "Config File (%s):\n",
            configargparse._DEFAULTS_SOURCE_KEY: "Defaults:\n"
        }

        r = StringIO()
        for source, settings in self._source_to_settings.items():
            source = source.split("|")
            source = source_key_to_display_value_map[source[0]] % tuple(source[1:])
            r.write(source)
            for key, (action, value) in settings.items():
                if key:
                    if key in self.fields_to_sanitize or action.option_strings[0] in self.fields_to_sanitize:
                        value = '****'
                    r.write("  {:<19}{}\n".format(key + ":", value))
                else:
                    if isinstance(value, str):
                        r.write("  %s\n" % value)
                    elif isinstance(value, list):
                        value = list(value)  # copy
                        if source == 'Command Line Args: ':
                            index = 0
                            while index < len(value):
                                if value[index] in self.fields_to_sanitize:
                                    index += 1
                                    value[index] = '****'
                                index += 1
                        r.write("  %s\n" % ' '.join(value))

        return r.getvalue()

    def write_config_file(self, parsed_namespace, output_file_paths, exit_after=False):
        """
        Write the given settings to output files. Overrides write_config_file from the class ArgumentParser for
        correcting types of some attributes (example: check, skip_check)

        :param parsed_namespace: namespace object created within parse_known_args()
        :param output_file_paths: any number of file paths to write the config to
        :param exit_after: whether to exit the program after writing the config files
        """
        for output_file_path in output_file_paths:
            # validate the output file path
            try:
                with self._config_file_open_func(output_file_path, "w") as output_file:
                    pass
            except IOError as e:
                raise ValueError("Couldn't open {} for writing: {}".format(
                    output_file_path, e))
        if output_file_paths:
            # generate the config file contents
            config_items = self.get_items_for_config_file_output(
                self._source_to_settings, parsed_namespace)
            # convert check, skip_check, soft_fail_on and hard_fail_on to list
            if 'check' in config_items.keys():
                config_items['check'] = config_items['check'][0].split(",")
            if 'skip-check' in config_items.keys():
                config_items['skip-check'] = config_items['skip-check'][0].split(",")
            if 'soft-fail-on' in config_items.keys():
                config_items['soft-fail-on'] = config_items['soft-fail-on'][0].split(",")
            if 'hard-fail-on' in config_items.keys():
                config_items['hard-fail-on'] = config_items['hard-fail-on'][0].split(",")
            # convert strings to booleans
            for k in config_items.keys():
                config_items[k] = convert_str_to_bool(config_items[k])

            file_contents = self._config_file_parser.serialize(config_items)
            for output_file_path in output_file_paths:
                with self._config_file_open_func(output_file_path, "w") as output_file:
                    output_file.write(file_contents)
            message = "Wrote config file to " + ", ".join(output_file_paths)
            if exit_after:
                self.exit(0, message)
            else:
                print(message)

