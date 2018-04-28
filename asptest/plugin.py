import pytest

from .commons import ASPException
from .parsers import asp_parse_blocks, asp_parse_test_case
from .hooks import pytest_addoption, pytest_collect_file, pytest_collection_modifyitems
from .classes import ASPFile, ASPItem


# from pprint import pprint
# print('TEST PARSE BLOCK:')
# pprint(tuple(asp_parse_blocks(open('examples/dumbasp.lp'))))
# print('TEST PARSE TEST CASE:')
# pprint(tuple(asp_parse_test_case(open('examples/test-two-in-one.lp'))))
