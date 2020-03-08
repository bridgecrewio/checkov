import sys
import logging
from copy import deepcopy
import six

LOGGER = logging.getLogger(__name__)


class TemplateAttributeError(AttributeError):
    """ Custom error to capture Attribute Errors in the Template """


def create_str_node_class(cls):
    """
    Create string node class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark

        # pylint: disable=bad-classmethod-argument, unused-argument
        def __new__(self, x, start_mark, end_mark):
            if sys.version_info >= (3, 0):
                return cls.__new__(self, x)

            if isinstance(x, six.string_types):
                return cls.__new__(self, x.encode('ascii', 'ignore'))

            return cls.__new__(self, x)

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

        def __deepcopy__(self, memo):
            result = str_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            return result

        def __copy__(self):
            return self

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


def create_dict_node_class(cls):
    """
    Create dynamic node class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark
            self.condition_functions = ['Fn::If']

        def __deepcopy__(self, memo):
            result = dict_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for k, v in self.items():
                result[deepcopy(k)] = deepcopy(v, memo)

            return result

        def __copy__(self):
            return self

        def is_function_returning_object(self, mappings=None):
            """
                Check if an object is using a function that could return an object
                Return True when
                    Fn::Select:
                    - 0  # or any number
                    - !FindInMap [mapname, key, value] # or any mapname, key, value
                Otherwise False
            """
            mappings = mappings or {}
            if len(self) == 1:
                for k, v in self.items():
                    if k in ['Fn::Select']:
                        if isinstance(v, list):
                            if len(v) == 2:
                                p_v = v[1]
                                if isinstance(p_v, dict):
                                    if len(p_v) == 1:
                                        for l_k in p_v.keys():
                                            if l_k == 'Fn::FindInMap':
                                                return True

            return False

        def get(self, key, default=None):
            """ Override the default get """
            if isinstance(default, dict):
                default = dict_node(default, self.start_mark, self.end_mark)
            return super(node_class, self).get(key, default)

        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []
            value = self.get(key, default)
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]

            results = []
            for sub_v, sub_path in value.items_safe(path + [key]):
                if isinstance(sub_v, type_t) or not type_t:
                    results.append((sub_v, sub_path))

            return results

        def items_safe(self, path=None, type_t=()):
            """Get items while handling IFs"""
            path = path or []
            if len(self) == 1:
                for k, v in self.items():
                    if k == 'Fn::If':
                        if isinstance(v, list):
                            if len(v) == 3:
                                for i, if_v in enumerate(v[1:]):
                                    if isinstance(if_v, dict):
                                        # yield from if_v.items_safe(path[:] + [k, i - 1])
                                        # Python 2.7 support
                                        for items, p in if_v.items_safe(path[:] + [k, i + 1]):
                                            if isinstance(items, type_t) or not type_t:
                                                yield items, p
                                    elif isinstance(if_v, list):
                                        if isinstance(if_v, type_t) or not type_t:
                                            yield if_v, path[:] + [k, i + 1]
                                    else:
                                        if isinstance(if_v, type_t) or not type_t:
                                            yield if_v, path[:] + [k, i + 1]
                    elif not (k == 'Ref' and v == 'AWS::NoValue'):
                        if isinstance(self, type_t) or not type_t:
                            yield self, path[:]
            else:
                if isinstance(self, type_t) or not type_t:
                    yield self, path[:]

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


def create_dict_list_class(cls):
    """
    Create dynamic list class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark
            self.condition_functions = ['Fn::If']

        def __deepcopy__(self, memo):
            result = list_node([], self.start_mark, self.end_mark)
            memo[id(self)] = result
            for _, v in enumerate(self):
                result.append(deepcopy(v, memo))

            return result

        def __copy__(self):
            return self

        def items_safe(self, path=None, type_t=()):
            """Get items while handling IFs"""
            path = path or []
            for i, v in enumerate(self):
                if isinstance(v, dict):
                    for items, p in v.items_safe(path[:] + [i]):
                        if isinstance(items, type_t) or not type_t:
                            yield items, p
                else:
                    if isinstance(v, type_t) or not type_t:
                        yield v, path[:] + [i]

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


str_node = create_str_node_class(str)
dict_node = create_dict_node_class(dict)
list_node = create_dict_list_class(list)
