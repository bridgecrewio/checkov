from __future__ import annotations
import json
import logging
from typing import Any

from schema import Schema, Optional, Or, Forbidden, SchemaError  # type: ignore

schema = Schema({Optional('name'): str,
                 Optional('on'): Or(dict, list, str),
                 Optional('jobs'): {
                     Optional('name'): str,
                     Optional('runs-on'): Or(str, list),
                     Forbidden('steps'): list
                 }}, ignore_extra_keys=True)


def is_schema_valid(config: dict[str, Any] | list[dict[str, Any]]) -> bool:
    valid = False
    try:
        schema.validate(config)
        valid = True
    except SchemaError as e:
        logging.info(f'Given entity configuration does not match the schema\n'
                     f'config={json.dumps(config, indent=4)}\n'
                     f'schema={json.dumps(schema.json_schema("https://example.com/my-schema.json"), indent=4)}')
        logging.info(f'Error: {e}', exc_info=e)
    finally:
        return valid
