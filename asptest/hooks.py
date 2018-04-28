"""Pytest hooks implementations.

"""

import pytest
from .commons import ASPException
from .parsers import asp_parse_test_case
from .classes import ASPFile, ASPItem


def pytest_addoption(parser):
    """Add option to the CLI"""
    group = parser.getgroup('asptest')
    group.addoption(
        '--uid-tests-dir',
        type=str,
        dest='asptest_uid_tests_dir',
        default='.',
        help='Where to find the test*.lp files for all uids.',
    )


def pytest_collect_file(parent, path):
    """Collect all lp files. They will give hint about tests to perform"""
    if path.ext == '.lp' and not path.basename.startswith('test'):
        return ASPFile(path, parent)


def pytest_collection_modifyitems(session, config, items):
    """Populate all items with their test case, found using config"""
    uid_dir = config.getoption('asptest_uid_tests_dir')

    def get_test_case(uid:str, fname:str) -> (str, tuple) or None:
        try:
            with open('{}/test-{}.lp'.format(uid_dir, uid)) as fd:
                return tuple(asp_parse_test_case(fd))
        except FileNotFoundError as err:
            if uid != fname:
                raise err
            else:
                pass  # nothing to do, it's optional

    # for each ASPItem, compute the item.uid, and give it to him
    asp_items = (item for item in items if isinstance(item, ASPItem))
    for item in asp_items:
        item.test_case = get_test_case(item.uid, item.fname)  # give item its test_case
