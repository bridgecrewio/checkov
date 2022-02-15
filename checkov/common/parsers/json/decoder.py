import logging
from json import JSONDecoder
from json.decoder import WHITESPACE, WHITESPACE_STR, BACKSLASH, STRINGCHUNK, JSONArray
from typing import List

from json.scanner import NUMBER_RE

from checkov.common.parsers.node import StrNode, DictNode, ListNode
from checkov.common.parsers.json.errors import NullError, DuplicateError, DecodeError


class Mark(object):
    """Mark of line and column"""
    line = 1
    column = 1

    def __init__(self, line, column):
        self.line = line
        self.column = column


# pylint: disable=W0102
# Exception based on builtin Python Function
def py_scanstring(s, end, strict=True,
                  _b=BACKSLASH, _m=STRINGCHUNK.match):
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.
    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise DecodeError('Unterminated string starting at', s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            _append(content)
        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == '"':
            break
        if terminator != '\\':
            if strict:
                msg = 'Invalid control character {0!r} at'.format(terminator)
                raise DecodeError(msg, s, end)
            _append(terminator)
            continue
        try:
            esc = s[end]
        except IndexError:
            raise DecodeError('Unterminated string starting at', s, begin)
        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\escape: {0!r}'.format(esc)
                raise DecodeError(msg, s, end)
            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 0xd800 <= uni <= 0xdbff and s[end:end + 2] == '\\u':
                uni2 = _decode_uXXXX(s, end + 1)
                if 0xdc00 <= uni2 <= 0xdfff:
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    end += 6
            # pylint: disable=undefined-variable
            try:
                char = unichr(uni)
            except NameError:
                char = chr(uni)
        _append(char)
    return ''.join(chunks), end


def _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    if len(esc) == 4 and esc[1] not in 'xX':
        try:
            return int(esc, 16)
        except ValueError:
            pass
    msg = 'Invalid \\uXXXX escape'
    raise DecodeError(msg, s, pos)


def py_make_scanner(context):
    """
        Make python based scanner
        For this use case we will not use the C based scanner
    """
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    # pylint: disable=R0911
    # Based on Python standard function
    def _scan_once(string, idx):
        """ Scan once internal function """
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx)

        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        if nextchar == '{':
            return parse_object(
                (string, idx + 1), strict,
                scan_once, object_hook, object_pairs_hook, memo)
        if nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        if nextchar == 'n' and string[idx:idx + 4] == 'null':
            return None, idx + 4
        if nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        if nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5

        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return res, m.end()
        if nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            return parse_constant('NaN'), idx + 3
        if nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            return parse_constant('Infinity'), idx + 8
        if nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            return parse_constant('-Infinity'), idx + 9

        raise StopIteration(idx)

    def scan_once(string, idx):
        """ Scan Once"""
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return _scan_once


def find_indexes(s, ch='\n'):
    """Finds all instances of given char and returns list of indexes """
    return [i for i, ltr in enumerate(s) if ltr == ch]


def count_occurrences(arr, key):
    """Binary search indexes to replace str.count """
    n = len(arr)
    left = 0
    right = n - 1
    count = 0

    while (left <= right):
        mid = int((right + left) / 2)

        if (arr[mid] <= key):
            count = mid + 1
            left = mid + 1
        else:
            right = mid - 1
    return count


def largest_less_than(indexes: List[int], line_num: int, pos: int) -> int:
    """Replacement func for python str.rfind using indexes """
    return indexes[line_num - 1] if indexes and count_occurrences(indexes, pos) else -1


def get_beg_end_mark(s, start, end, indexes):
    """Get the Start and End Mark """
    beg_lineno = count_occurrences(indexes, start)
    beg_colno = start - largest_less_than(indexes, beg_lineno, start)
    beg_mark = Mark(beg_lineno, beg_colno)

    offset = 1 if len(indexes) > 1 else 0
    end_lineno = count_occurrences(indexes, end) - offset
    end_colno = end - largest_less_than(indexes, end_lineno, end)
    end_mark = Mark(end_lineno, end_colno)

    return beg_mark, end_mark


class Decoder(JSONDecoder):
    """
    Converts a json string, where datetime and timedelta objects were converted
    into strings using the DateTimeAwareJSONEncoder, into a python object.
    """

    def __init__(self, *args, **kwargs):
        self.allow_nulls = kwargs.pop("allow_nulls", True)
        JSONDecoder.__init__(self, *args, **kwargs)
        self.parse_object = self.json_object
        self.parse_array = self.json_array
        self.parse_string = py_scanstring
        self.memo = {}
        self.object_pairs_hook = self.check_duplicates
        self.scan_once = py_make_scanner(self)
        self.newline_indexes = []

    def decode(self, s):
        """Overridden to retrieve indexes """
        self.newline_indexes = find_indexes(s)
        obj = super().decode(s)
        return obj

    def json_array(self, s_and_end, scan_once, **kwargs):
        """ Convert JSON array to be a list_node object """
        values, end = JSONArray(s_and_end, scan_once, **kwargs)
        s, start = s_and_end
        beg_mark, end_mark = get_beg_end_mark(s, start, end, self.newline_indexes)
        return ListNode(values, beg_mark, end_mark), end

    def json_object(self, s_and_end, strict, scan_once, object_hook, object_pairs_hook,
                    memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
        """ Custom Cfn JSON Object to store keys with start and end times """
        s, end = s_and_end
        orginal_end = end
        pairs = []
        pairs_append = pairs.append
        # Backwards compatibility
        if memo is None:
            memo = {}
        memo_get = memo.setdefault
        # Use a slice to prevent IndexError from being raised, the following
        # check will raise a more specific ValueError if the string is empty
        nextchar = s[end:end + 1]
        # Normally we expect nextchar == '"'
        if nextchar != '"':
            if nextchar in _ws:
                end = _w(s, end).end()
                nextchar = s[end:end + 1]
            # Trivial empty object
            if nextchar == '}':
                if object_pairs_hook is not None:
                    try:
                        beg_mark, end_mark = get_beg_end_mark(s, orginal_end, end + 1, self.newline_indexes)
                        result = object_pairs_hook(pairs, beg_mark, end_mark)
                        return result, end + 1
                    except DuplicateError as err:
                        raise DecodeError('Duplicate found {}'.format(err), s, end)
                    except NullError as err:
                        raise DecodeError('Null Error {}'.format(err), s, end)
                pairs = {}
                if object_hook is not None:
                    beg_mark, end_mark = get_beg_end_mark(s, orginal_end, end + 1, self.newline_indexes)
                    pairs = object_hook(pairs, beg_mark, end_mark)
                return pairs, end + 1

            if nextchar != '"':
                raise DecodeError('Expecting property name enclosed in double quotes', s, end)
        end += 1
        while True:
            begin = end - 1
            key, end = py_scanstring(s, end, strict)
            # print(lineno, colno, obj)
            # print(key, lineno, colno)
            key = memo_get(key, key)
            # To skip some function call overhead we optimize the fast paths where
            # the JSON key separator is ": " or just ":".
            if s[end:end + 1] != ':':
                end = _w(s, end).end()
                if s[end:end + 1] != ':':
                    raise DecodeError('Expecting \':\' delimiter', s, end)
            end += 1

            try:
                if s[end] in _ws:
                    end += 1
                    if s[end] in _ws:
                        end = _w(s, end + 1).end()
            except IndexError:
                pass

            beg_mark, end_mark = get_beg_end_mark(s, begin, begin + len(key), self.newline_indexes)
            try:
                value, end = scan_once(s, end)
            except StopIteration as err:
                logging.error(err)
                raise DecodeError('Expecting value', s, end_mark.line)
            key_str = StrNode(key, beg_mark, end_mark)
            pairs_append((key_str, value))
            try:
                nextchar = s[end]
                if nextchar in _ws:
                    end = _w(s, end + 1).end()
                    nextchar = s[end]
            except IndexError:
                nextchar = ''
            end += 1

            if nextchar == '}':
                break
            if nextchar != ',':
                raise DecodeError('Expecting \',\' delimiter', s, end - 1)
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
            end += 1
            if nextchar != '"':
                raise DecodeError(
                    'Expecting property name enclosed in double quotes', s, end - 1)
        if object_pairs_hook is not None:
            try:
                beg_mark, end_mark = get_beg_end_mark(s, orginal_end, end, self.newline_indexes)
                result = object_pairs_hook(pairs, beg_mark, end_mark)
            except DuplicateError as err:
                raise DecodeError('Duplicate found {}'.format(err), s, begin, key)
            except NullError as err:
                raise DecodeError('Null Error {}'.format(err), s, begin, key)
            return result, end

        pairs = dict(pairs)
        if object_hook is not None:
            beg_mark, end_mark = get_beg_end_mark(s, orginal_end, end, self.newline_indexes)
            pairs = object_hook(pairs, beg_mark, end_mark)
        return pairs, end

    def check_duplicates(self, ordered_pairs, beg_mark, end_mark):
        """
            Check for duplicate keys on the current level, this is not desirable
            because a dict does not support this. It overwrites it with the last
            occurance, which can give unexpected results
        """
        mapping = DictNode({}, beg_mark, end_mark)
        for key, value in ordered_pairs:
            if not self.allow_nulls and value is None:
                raise NullError('"{}"'.format(key))
            if key in mapping:
                raise DuplicateError('"{}"'.format(key))
            mapping[key] = value
        return mapping
