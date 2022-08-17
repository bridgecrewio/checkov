from schema import Schema, Optional, Or, Forbidden  # type: ignore

schema = Schema({
    Optional('name'): str,
    Optional('on'): Or(dict, list, str),
    Optional('jobs'): {
        Optional('name'): str,
        Optional('runs-on'): Or(str, list),
        Forbidden('steps'): list
    }
}, ignore_extra_keys=True)
