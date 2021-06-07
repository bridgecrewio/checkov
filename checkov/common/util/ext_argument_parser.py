import configargparse

from checkov.common.util.type_forcers import convert_str_to_bool


class ExtArgumentParser(configargparse.ArgumentParser):

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
            # convert check and skip_check to list
            if 'check' in config_items.keys():
                config_items['check'] = config_items['check'][0].split(",")
            if 'skip-check' in config_items.keys():
                config_items['skip-check'] = config_items['skip-check'][0].split(",")
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

