"""Tests for optional_type_parser.

Type constraint strings below mirror checkov's HCL parser output (pyhcl2).
Each object nesting level adds a backslash-escape layer around inner quotes,
e.g. ``\\'field\\'`` at level 1, ``\\\\\\'field\\\\\\'`` at level 2.  This is
unavoidable -- the strings must match real parser output exactly.
"""
from __future__ import annotations

from checkov.terraform.graph_builder.variable_rendering.optional_type_parser import (
    _parse_optional_defaults_from_type,
    apply_optional_defaults,
)


class TestParseOptionalDefaultsFromType:
    """Tests for parsing optional() defaults from type constraint strings."""

    def test_list_object_with_string_and_number_defaults(self) -> None:
        type_str = """${list(object({'name': '${string}', 'type': '${optional(string,"RSA-HSM")}', 'size': '${optional(number,2048)}'}))}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"type": "RSA-HSM", "size": 2048}

    def test_object_with_string_and_number_defaults(self) -> None:
        type_str = """${object({'name': '${string}', 'region': '${optional(string,"us-east-1")}', 'port': '${optional(number,443)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"region": "us-east-1", "port": 443}

    def test_object_with_bool_default(self) -> None:
        type_str = """${object({'name': '${string}', 'debug': '${optional(bool,True)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"debug": True}

    def test_object_with_false_bool_default(self) -> None:
        type_str = """${object({'name': '${string}', 'disabled': '${optional(bool,False)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"disabled": False}

    def test_optional_without_default(self) -> None:
        type_str = """${object({'name': '${string}', 'label': '${optional(string)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {}

    def test_no_optional_fields(self) -> None:
        type_str = """${object({'name': '${string}', 'count': '${number}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {}

    def test_none_type_str(self) -> None:
        result = _parse_optional_defaults_from_type(None)
        assert result == {}

    def test_list_wrapped_type_str(self) -> None:
        """The HCL parser wraps type in a list."""
        type_str = ["""${object({'port': '${optional(number,443)}'})}"""]
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"port": 443}

    def test_set_of_objects(self) -> None:
        type_str = """${set(object({'port': '${optional(number,443)}'}))}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"port": 443}

    def test_map_of_objects(self) -> None:
        type_str = """${map(object({'port': '${optional(number,80)}'}))}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"port": 80}

    def test_string_with_comma(self) -> None:
        type_str = """${object({'label': '${optional(string,"a, b")}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"label": "a, b"}

    def test_empty_map_default(self) -> None:
        type_str = """${object({'tags': '${optional(map(string),{})}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"tags": {}}

    def test_empty_list_default(self) -> None:
        type_str = """${object({'items': '${optional(list(string),[])}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"items": []}

    def test_list_with_values_default(self) -> None:
        type_str = """${object({'items': '${optional(list(string),["a","b"])}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"items": ["a", "b"]}

    def test_map_with_values_default(self) -> None:
        type_str = """${object({'tags': '${optional(map(string),{env = "prod"})}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"tags": {"env": "prod"}}

    def test_null_default(self) -> None:
        type_str = """${object({'value': '${optional(string,null)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"value": None}

    def test_float_default(self) -> None:
        type_str = """${object({'ratio': '${optional(number,0.5)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"ratio": 0.5}

    def test_without_dollar_brace_wrapper(self) -> None:
        """Handle type strings without the ${...} wrapper."""
        type_str = "object({'port': '${optional(number,8080)}'})"
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"port": 8080}

    def test_empty_string_default(self) -> None:
        type_str = """${object({'label': '${optional(string,"")}'})  }"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"label": ""}

    def test_negative_number_default(self) -> None:
        type_str = """${object({'offset': '${optional(number,-1)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"offset": -1}

    def test_string_with_colon(self) -> None:
        type_str = """${object({'addr': '${optional(string,"host:port")}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"addr": "host:port"}

    def test_unresolvable_default_returns_as_string(self) -> None:
        """Default values that can't be parsed (e.g., variable references) pass through as strings."""
        type_str = """${object({'label': '${optional(string,local.default_label)}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"label": "local.default_label"}

    def test_optional_with_complex_object_default(self) -> None:
        """Optional field whose default is a populated object/map."""
        type_str = """${object({'config': '${optional(object({\\\'host\\\': \\\'${string}\\\', \\\'port\\\': \\\'${number}\\\'}),{host = "localhost", port = 8080})}'})}"""
        result = _parse_optional_defaults_from_type(type_str)
        assert result == {"config": {"host": "localhost", "port": 8080}}

    def test_malformed_unclosed_brace(self) -> None:
        """Malformed type string with unclosed brace returns empty defaults."""
        result = _parse_optional_defaults_from_type("${object({unclosed")
        assert result == {}


class TestApplyOptionalDefaults:
    def test_object_dict_merge(self) -> None:
        value = {"name": "test"}
        type_str = """${object({'name': '${string}', 'port': '${optional(number,443)}'})}"""
        result = apply_optional_defaults(value, type_str)
        assert result == {"name": "test", "port": 443}
        # Verify original is not mutated
        assert "port" not in value

    def test_list_of_objects_merge(self) -> None:
        value = [{"name": "examplekey"}]
        type_str = """${list(object({'name': '${string}', 'type': '${optional(string,"RSA-HSM")}', 'size': '${optional(number,2048)}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == [{"name": "examplekey", "type": "RSA-HSM", "size": 2048}]
        # Verify original is not mutated
        assert "type" not in value[0]

    def test_list_of_objects_multiple_items(self) -> None:
        value = [{"name": "key1"}, {"name": "key2", "type": "EC-HSM"}]
        type_str = """${list(object({'name': '${string}', 'type': '${optional(string,"RSA-HSM")}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == [
            {"name": "key1", "type": "RSA-HSM"},
            {"name": "key2", "type": "EC-HSM"},  # existing value preserved
        ]

    def test_map_of_objects_merge(self) -> None:
        value = {"key1": {"name": "test"}}
        type_str = """${map(object({'name': '${string}', 'port': '${optional(number,80)}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == {"key1": {"name": "test", "port": 80}}

    def test_none_type_str(self) -> None:
        value = {"name": "test"}
        result = apply_optional_defaults(value, None)
        assert result == {"name": "test"}

    def test_empty_list(self) -> None:
        value: list[dict[str, str]] = []
        type_str = """${list(object({'port': '${optional(number,80)}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == []

    def test_non_dict_value_unchanged(self) -> None:
        value = "some_string"
        type_str = """${object({'port': '${optional(number,80)}'})}"""
        result = apply_optional_defaults(value, type_str)
        assert result == "some_string"

    def test_set_of_objects_merge(self) -> None:
        value = [{"name": "test"}]
        type_str = """${set(object({'name': '${string}', 'port': '${optional(number,443)}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == [{"name": "test", "port": 443}]

    def test_list_wrapped_type_str(self) -> None:
        """The HCL parser wraps the type attribute in a list."""
        value = {"name": "test"}
        type_str = ["""${object({'name': '${string}', 'port': '${optional(number,443)}'})}"""]
        result = apply_optional_defaults(value, type_str)
        assert result == {"name": "test", "port": 443}

    def test_tuple_of_objects_merge(self) -> None:
        value = [{"name": "test"}]
        type_str = """${tuple(object({'name': '${string}', 'port': '${optional(number,8080)}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == [{"name": "test", "port": 8080}]

    def test_double_wrapped_list_default(self) -> None:
        """The HCL parser wraps list defaults as [[{...}]]."""
        value = [[{"name": "examplekey"}]]
        type_str = """${list(object({'name': '${string}', 'type': '${optional(string,"RSA-HSM")}'}))}"""
        # The outer list is unwrapped elsewhere -- apply_optional_defaults gets the inner list
        result = apply_optional_defaults(value, type_str)
        # apply_optional_defaults iterates the outer list; inner list items aren't dicts
        # This case is handled upstream when the default value is unwrapped
        assert result == [[{"name": "examplekey"}]]

    def test_simple_type_passthrough(self) -> None:
        """A simple type like 'string' has no object -- value passes through unchanged."""
        result = apply_optional_defaults("hello", "string")
        assert result == "hello"

    # --- Nested object tests (recursive descent) ---

    def test_nested_object_defaults(self) -> None:
        """Level 2: object containing an inner object with optional fields."""
        value = {"name": "test", "network": {}}
        type_str = """${object({'name': '${string}', 'network': '${object({\\\'port\\\': \\\'${optional(number,443)}\\\', \\\'protocol\\\': \\\'${optional(string,"https")}\\\'})}'})  }"""
        result = apply_optional_defaults(value, type_str)
        assert result == {"name": "test", "network": {"port": 443, "protocol": "https"}}
        assert value["network"] == {}

    def test_nested_object_in_list(self) -> None:
        """Recursion through list items into nested objects."""
        value = [{"name": "a", "inner": {}}, {"name": "b", "inner": {"port": 80}}]
        type_str = """${list(object({'name': '${string}', 'inner': '${object({\\\'port\\\': \\\'${optional(number,443)}\\\'})}'}))}"""
        result = apply_optional_defaults(value, type_str)
        assert result == [
            {"name": "a", "inner": {"port": 443}},
            {"name": "b", "inner": {"port": 80}},  # existing value preserved
        ]

    def test_nested_optional_map_of_objects(self) -> None:
        """Recursion through optional(map(object({...})))."""
        # Logical: object({ databases: optional(map(object({ collections: map(object({
        #            partition_key: string, throughput: optional(number, 100) })) })), {}) })
        value = {"name": "test", "databases": {"db1": {"collections": {"col1": {"partition_key": "/id"}}}}}
        type_str = """${object({'name': '${string}', 'databases': '${optional(map(object({\\\'collections\\\': \\\'${map(object({\\\\\\\'partition_key\\\\\\\': \\\\\\\'${string}\\\\\\\', \\\\\\\'throughput\\\\\\\': \\\\\\\'${optional(number,100)}\\\\\\\'}))}\\\'})),{})}'})  }"""
        result = apply_optional_defaults(value, type_str)
        assert result["databases"]["db1"]["collections"]["col1"] == {"partition_key": "/id", "throughput": 100}

    def test_three_level_nesting(self) -> None:
        """3 levels: object -> object -> list(object) with optional at the deepest level."""
        # Logical: object({ key_vault: object({ keys: list(object({
        #            name: string, key_type: optional(string, "RSA-HSM"), key_size: optional(number, 2048) })) }) })
        value = {"key_vault": {"keys": [{"name": "mykey"}]}}
        type_str = """${object({'key_vault': '${object({\\\'keys\\\': \\\'${list(object({\\\\\\\'name\\\\\\\': \\\\\\\'${string}\\\\\\\', \\\\\\\'key_type\\\\\\\': \\\\\\\'${optional(string,"RSA-HSM")}\\\\\\\', \\\\\\\'key_size\\\\\\\': \\\\\\\'${optional(number,2048)}\\\\\\\'}))}\\\'})}'})}"""
        result = apply_optional_defaults(value, type_str)
        assert result == {"key_vault": {"keys": [{"name": "mykey", "key_type": "RSA-HSM", "key_size": 2048}]}}

    def test_nested_no_mutation(self) -> None:
        """Verify original nested value is not mutated."""
        inner = {"name": "test"}
        value = {"wrapper": {"items": [inner]}}
        type_str = """${object({'wrapper': '${object({\\\'items\\\': \\\'${list(object({\\\\\\\'name\\\\\\\': \\\\\\\'${string}\\\\\\\', \\\\\\\'port\\\\\\\': \\\\\\\'${optional(number,80)}\\\\\\\'}))}\\\'})}'})}"""
        result = apply_optional_defaults(value, type_str)
        assert result["wrapper"]["items"][0] == {"name": "test", "port": 80}
        assert "port" not in inner

    def test_all_optional_fields_present_returns_unchanged(self) -> None:
        """When all optional keys exist at all levels, value is unchanged."""
        value = {"name": "test", "port": 80, "inner": {"x": 1}}
        type_str = """${object({'name': '${string}', 'port': '${optional(number,443)}', 'inner': '${object({\\\'x\\\': \\\'${optional(number,99)}\\\'})}'})  }"""
        result = apply_optional_defaults(value, type_str)
        assert result == {"name": "test", "port": 80, "inner": {"x": 1}}

    def test_multi_element_list_type_str(self) -> None:
        """Multi-element list type_str is ignored (only single-element expected from HCL parser)."""
        assert apply_optional_defaults({"x": 1}, ["a", "b"]) == {"x": 1}

    def test_non_string_type_str(self) -> None:
        """Non-string, non-list type_str (e.g. int) passes value through unchanged."""
        assert apply_optional_defaults({"x": 1}, 42) == {"x": 1}
