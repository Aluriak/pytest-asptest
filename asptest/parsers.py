"""Definition of the parsers used to extract test cases
and testable blocks from ASP source code.

"""

import re


def asp_parse_blocks(lines:[str], filename:str,uid_line:str='% TEST: ',
                     uid_name:str='% TESTNAME: ') -> [({str}, str, str)]:
    """Yield blocks of ASP source code with their uid, if any, and a (unique) name"""
    regex_uid = re.compile(r'^% TEST(\s+[a-zA-Z0-9_.-]+)?: ')
    block_line, block, uids, test_name = 1, [], set(), None

    def format_yield():
        if test_name:
            block_name = 'block ' + test_name.strip()
        else:  # use the line numbers
            block_name = 'line {}-{}'.format(block_line, idx_line-1)
        return uids | {filename}, block, block_name

    for idx_line, line in enumerate(lines, start=1):
        if not line.strip():
            yield format_yield()
            block_line, block, uids, test_name = None, [], set(), None
            continue

        if block_line is None:
            block_line = idx_line

        match_uid = regex_uid.match(line)
        if match_uid:
            if uids:  # already defined uids
                raise ASPException("Multiple definition of TESTNAME at line {} "
                                   "for block starting at line {}"
                                   "".format(idx_line, block_line))
            start_index_uids = match_uid.span()[1]
            test_name = match_uid.groups()[0]
            uids = frozenset(map(str.strip, line[start_index_uids:].split(',')))
        else:  # any non empty line
            block.append(line)
    if block:
        yield format_yield()


def asp_parse_test_case(lines:[str]) -> [(str, [(bool, str)])]:
    """Yield test cases as (input, outputs, strict).

    input -- an ASP program ready to be grounded
    outputs -- iterable describing content of each expected answer set,
               with a boolean indicating if the given content is a subset of
               the expected answer or not.

    """
    START_INPUT = '% INPUT'
    START_OUTPUT = '% OUTPUT'
    START_STRICT_OUTPUT = '% STRICT OUTPUT'
    INSATISFIABLE = '% INSATISFIABLE'

    current_state, data_input, data_output = None, [], []

    def format_yield():
        return ''.join(data_input), tuple((''.join(lines), strict) for lines, strict in data_output)

    for idx, line in enumerate(lines, start=1):
        # detect end of test case
        if line.startswith((START_INPUT, INSATISFIABLE)):
            if data_output:
                yield format_yield()
                current_state, data_input, data_output = None, [], []

        if line.startswith(START_INPUT):
            current_state = data_input
        elif line.startswith(START_OUTPUT):
            data_output.append(([], False))  # new output lines, non strict
            current_state = data_output[-1][0]
        elif line.startswith(START_STRICT_OUTPUT):
            data_output.append(([], True))  # new output lines, strict
            current_state = data_output[-1][0]
        elif line.startswith(INSATISFIABLE):
            current_state = None
        elif line.strip():
            if current_state is not None:
                current_state.append(line)
            else:
                pass  # non empty line that doesn't belong to any place

    if data_output:
        yield format_yield()
