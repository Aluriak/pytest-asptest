class ASPException(Exception):
    """Custom exception for error reporting."""


def tuple_as_atom(atom:tuple) -> str:
    """Return readable version of given atom.

    >>> tuple_as_atom(('a', (3,)))
    'a(3)'
    >>> tuple_as_atom(('bcd', ('bcd',12)))
    'bcd(bcd,12)'

    """
    assert len(atom) == 2
    return '{}({})'.format(atom[0], ','.join(map(str, atom[1])))
