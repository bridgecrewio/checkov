class DuplicateError(Exception):
    """
    Error thrown when the template contains duplicates
    """


class NullError(Exception):
    """
    Error thrown when the template contains Nulls
    """


class DecodeError(ValueError):
    """Subclass of ValueError with the following additional properties:
    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos
    """
    # Note that this exception is used from _json

    def __init__(self, msg, doc, pos, key=' '):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)
