---
layout: default
published: true
title: Sharing Policies
order: 9
---

# Configure checkov

The fastest way to configure checkov is by using cli options.
They give you all available options.
You can get an overview about those by executing `checkov --help` or by looking into [Getting Started](../1.Introduction/Getting%20Started.md).

You can run checkov repeatedly with the same configuration by using configuration files.
Checkov supports two formats in which you can define the configuration.
Both have the same capabilities so you may choose what fits for you.

- **yaml configuration**: A yaml file containing one object representing the configuration
- **ini configuration**: The format used in `tox.ini` or `setup.cfg`. You can ruse these files to configure checkov as you may already do with other tools.

Checkov will detect which format you are using based of its content.

## The configuration file

The configuration contains a subset of those options available via cli arguments.
You are not forced to define every option as you are not in the cli.
You should check the [merging behavior](#merging-configurations) how this influences the configuration.  

After parsing the cli arguments, checkov loads all available configuration files.
After combining these with the cli arguments, the final configuration is now available and will be processed.
This even happens when you use e.g. `checkov --list`.
All the documentation on arguments like `--file` and `--directory` applies to the resulting config as well.

In the following sections, we show the arguments in more detail.
For information about the option itself, you should check `checkov --help` or [Getting Started](../1.Introduction/Getting%20Started.md).

### yaml

The yaml file contains one object.
The properties of this object define the configuration.
They are listed in the following table.


| cli option | name of the property | format | comment |
| ---------- | -------------------- | ------ | ------- |
| `--directory` | `directories` | list of strings or a string | The list is converted into a list with unique elements. Only the first occurence is preserved. |
| `--file` | `files` | list of strings or a string | The list is converted into a list with unique elements. Only the first occurence is preserved. |
| `--external-checks-dir` | `external_checks_dirs` | list of strings or a string | The list is converted into a list with unique elements. Only the first occurence is preserved. |
| `--external-checks-git` | `external_checks_gits` | list of strings or a string | The list is converted into a list with unique elements. Only the first occurence is preserved. |
| `--output` | `output` | string | See `checkov --help` for available options. |
| `--no-guide` | `no_guide` | boolean ||
| `--quiet` | `quiet` | boolean ||
| `--framework` | `framework` | string | See `checkov --help` for available options. |
| `--merging-behavior` | `merging_behavior` | string | See `checkov --help` for available options. |
| `--check` | `checks` | list of strings or a string | If it is a string, it is interpreted in the format as the cli argument would be. (Check ids are separated by just a comma e.g. CKV_1,CKV_2) If it is a list, the entries should be check ids. See `checkov --help` for the interaction with `--skip-check`. |
| `--skip-checks` | `skip_checks` | list of strings or a string | If it is a string, it is interpreted in the format as the cli argument would be. (Check ids are separated by just a comma e.g. CKV_1,CKV_2) If it is a list, the entries should be check ids. See `checkov --help` for the interaction with `--check`. |
| `--soft-fail` | `soft_fail` | boolean ||
| `--repo-id` | `repo_id` | string | See `checkov --help` for the expected format. |
| `--branch` | `branch` | string ||

See [the yaml specification](https://yaml.org/spec/) to learn about how to define the specific types.

### ini (Config)

This format can be used in combination with `tox.ini` or `setup.cfg`.
You define the checkov related configuration below the checkov block (`[checkov]`).
The default block is also considered.


| cli option | name of the property | format | comment |
| ---------- | -------------------- | ------ | ------- |
| `--directory` | `directories` | comma separated strings | All line breaks are removed before splitting at ",". In general quoting is not required. Only if the path contains leading or trailing white space, because whitespace around "," is removed. |
| `--file` | `files` | comma separated strings | All line breaks are removed before splitting at ",". In general quoting is not required. Only if the path contains leading or trailing white space, because whitespace around "," is removed. |
| `--external-checks-dir` | `external_checks_dirs` | comma separated strings | All line breaks are removed before splitting at ",". In general quoting is not required. Only if the path contains leading or trailing white space, because whitespace around "," is removed. |
| `--external-checks-git` | `external_checks_gits` | comma separated strings | All line breaks are removed before splitting at ",". In general quoting is not required. Only if the path contains leading or trailing white space, because whitespace around "," is removed. |
| `--output` | `output` | string | See `checkov --help` for available options. |
| `--no-guide` | `no_guide` | boolean ||
| `--quiet` | `quiet` | boolean ||
| `--framework` | `framework` | string | See `checkov --help` for available options. |
| `--merging-behavior` | `merging_behavior` | string | See `checkov --help` for available options. |
| `--check` | `checks` | comma separated strings | Interpreted like files and then joined again via "," to create the format of `--check`. See `checkov --help` for the interaction with `--skip-check`. |
| `--skip-checks` | `skip_checks` | list of strings or a string | Interpreted like files and then joined again via "," to create the format of `--skip-check`. See `checkov --help` for the interaction with `--check`. |
| `--soft-fail` | `soft_fail` | boolean ||
| `--repo-id` | `repo_id` | string | See `checkov --help` for the expected format. |
| `--branch` | `branch` | string ||


## Merging configurations

If you use a configuration, there is at least the need to combine it with the configuration done via cli.
We extended this to allow you to use multiple configuration files. (See the [default configuration files](#default-locations-where-checkov-searches-for-configuration-files))

The merging operation is in general ***not associative nor commutative***.
This means it depends in which order you combine three or more and also which one you merge the other matters.

Checkov solves this by defining a total ordering of the configuration files.
The one with the lover priority is merged into the one with higher priority.
Because of the total ordering, there are no configurations with the same priority.
When combining more then two, we always start with the lowest priority.
We do it this way, because the merging behavior is not changed.
The other way could case some unexpected behavior when using special merging strategies.

If we have the following files with descending priority A, B and C and we want to merge them into a single file, we first merge C into B.
The result is then merged into A to create the total result.

Now we look at the different strategies, how configurations could be merged.
They do not change when something is merged into it.

### Strategy: "union"

Keeps every single value options but creates a union of all those who support multiple values like `directories` or `checks`.
For those who are a list with unique elements, the parent values that do not occur in the child are appended.

The special case are `checks` and `skip_checks`.
A config containing both is invalid.
On a valid one, the one that is present is concatenating to the corresponding value at the parent.
The parent does not have to be valid.

### Strategy: "override"

Ignore the parent completely or in other words, the parent is overridden completely.
The configuration does not change.

### Strategy: "override_if_present"

If the value is present in the child, it overrides the value in the parent.
This is useful to use the parent for default values.

The special case are `checks` and `skip_checks`.
For this, to not override, both have to be not set.
Then both values are copied from the parent.
If the parent was invalid, the child becomes invalid.

### Strategy: "copy_parent"

Ignore the child and replace all values with the parent values.
This disables the child config.

## Specifying a configuration file

You can specify configuration files using the `--config-files` option.
There you can list an arbitrary amount of configuration files.
The order you use defines the order in which they are merged.
The help text states "in increasing priority".
This means that the first file is merged into the second one.
The result of this is then merged into the third one and so on.
Note that when you have configuration files in [the default location](#default-locations-where-checkov-searches-for-configuration-files), the result of merging the configurations from the default location, they are merged into the first listed configuration.

## Interaction with command line arguments

All the command line argument that are available in the configuration files are actually interpreted like a configuration file.
It's merging behavior is set with the `--merging-behavior` option.
By default it overrides the configuration files in the options that you set but keep the other once.
If you want to ignore all configuration files, you can use `--merging-behavior override`.

The command line arguments are the last part in the "merging chain".
The result of the files [you specified](#interaction-with-command-line-arguments) or if you didn't the one from [the default location](#default-locations-where-checkov-searches-for-configuration-files) is merged into the configuration defined by the command line arguments. 
In this way, the command line arguments have the highest priority.

## Default locations where checkov searches for configuration files

To allow you easy configuration, checkov searches some default locations for configuration files.
These are inside the project (local configuration) and global on your computer (global configuration).
All existing files are merged in ascending priority order.

### Global configuration files

There is just one global configuration file.
Depending on your os and environment one file is checked.

#### Windows

The global configuration file is stored in `~/checkov/config`.

#### Linux, MacOS (and everything else)

If you use a XDG based directory (determined by checking if `XDG_CONFIG_HOME` is set), the file must be at `$XDG_CONFIG_HOME/checkov/config`.
Otherwise it must be at `$HOME/.config/checkov/config`.
Usually this is the same.

### Local configuration files

These files must be in the working directory of checkov.
All the following files are checked and merged into the lower once.

- tox.ini
- setup.cfg
- .checkov.yml
- .checkov.yaml
- .checkov

E.g. you use tox.ini and also define .checkov.yaml and .checkov, then tox.ini is merged into .checkov.yaml and the result is merged into .checkov.

When you also have a global configuration file, this is merged into tox.ini in this case before it is merged itself.

The result of that is merged into the first listed configuration file in `--config-files` or, if this is not used, into the command line arguments.

## Summary

Configuration files are merged in the following order. "A -> B" denotes that A is merged into B.

"global configuration file" -> "local configuration files" -> "specified configuration files" -> "command line arguments"

The two middle parts can contain multiple files.
They are also merged but not in this group.
Let us expand the above one for the local default files tox.ini and .checkov and when you use `--config-files A B` on linux

(((($HOME/.config/checkov/config -> tox.ini) -> .config) -> A) -> B) -> "command line arguments" 