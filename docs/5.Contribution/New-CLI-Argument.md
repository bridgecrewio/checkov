# Contributing a new command line argument

For now this is just a check list for those, who added a new command line argument. Doing that will require some updates in other places. This should be a checklist to get all those places.

## Implementation

The main files for implementing new cli arguments are:

- [main.py](../../checkov/main.py) (see: `add_parser_args`)
- [config.py](../../checkov/config.py) (If it is reflected in the configuration of checkov.)

## Places to update

- [Config.md](../2.Concepts/Config.md)
- [Getting Started.md](../1.Introduction/Getting%20Started.md)
  - Run `checkov --help` and copy the command line arguments. 
