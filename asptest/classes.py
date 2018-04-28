"""Definitions of the classes and routines implementing the real thing,
the ASP source code testing.

"""

import pytest
import clyngor
import operator
import textwrap
from collections import defaultdict
from .commons import ASPException, tuple_as_atom
from .parsers import asp_parse_blocks


def verify_asp_code(source:str, answers:iter) -> (...):
    """Return a description of how bad the source performed to build the answer.
    """

    founds = frozenset(clyngor.solve(inline=source))
    answers = tuple((idx, source, next(clyngor.solve(inline=source)), strict)
                    for idx, (source, strict) in enumerate(answers, start=1))
    expecteds = frozenset((idx, answer) for idx, _, answer, strict in answers if not strict)
    strict_expecteds = frozenset((idx, answer) for idx, _, answer, strict in answers if strict)
    expecteds_enum = ((strict_expecteds, operator.ge), (expecteds, operator.eq))

    results = {
        'matched': [],  # pairs of found_idx, expected_idx
        'invalid': [],  # found_idx without matching expected_idx
        'unfound': [],  # expected_idx without matching expected_idx
        'overuse': {},  # expected_idx matching multiple found_idx
    }
    results['overuse'] = defaultdict(int)
    results['founds'] = {}  # map found_idx with its source
    results['expecteds'] = {idx: answer for idx, *answer in answers}
    matched_expected = set()
    matched_found = set()


    # print('SRC:', source)
    found_idx = 0  # handle insatisfiability cases
    for found_idx, found in enumerate(clyngor.solve(inline=source), start=1):
        results['founds'][found_idx] = found
        # print('FOUND:', found_idx, found)
        # print('ASSERT LBQ:', isinstance(found, frozenset))
        for expected_idx, source_expected, expected, strict in answers:
            operation = operator.eq if strict else operator.le
            # print('EXPECTED:', expected_idx, expected)
            # print('ASSERT LTE:', isinstance(expected, frozenset))
            # print('LAP:', found)
            # print('LAP:', expected)
            # print('LAP:', operation, operation(expected, found))
            if operation(expected, found):
                results['matched'].append((found_idx, expected_idx))
                if expected_idx in matched_expected:
                    results['overuse'][expected_idx] += 1
                matched_expected.add(expected_idx)
                matched_found.add(found_idx)
                break

    # detect founds that were not matched with anything
    total_found = frozenset(range(1, found_idx+1))
    results['invalid'] = total_found - frozenset(matched_found)
    # detect expecteds that were not matched with anything
    total_expected = frozenset(range(1, 1+len(answers)))
    results['unfound'] = total_expected - frozenset(matched_expected)
    # print('LTEQI:', results)

    # postprocess and return
    results['overuse'] = dict(results['overuse'])
    results['ok'] = (
        len(results['matched']) == len(answers) and
        not results['invalid'] and
        not results['unfound'] and
        not results['overuse']
    )
    return results


def repr_results(results:dict) -> str:
    if results['ok'] is True:
        yield 'OK'
        return
    LINE_HEAD_SIZE = 8
    answer_to_str = lambda a: ' '.join(map(tuple_as_atom, a))
    wrap = lambda t: textwrap.wrap(t, placeholder='[…]', max_lines=1,
                                   fix_sentence_endings=True)
    out = []
    nb_invalid = len(results['invalid'])
    nb_unfound = len(results['unfound'])
    nb_overuse = len(results['overuse'])
    if nb_invalid:
        yield ('A total of {} unexpected answer set{} found:'
               ''.format(nb_invalid, 's were' if nb_invalid > 1 else ' was'))
        for found_idx in sorted(results['invalid']):
            head = str(found_idx).ljust(LINE_HEAD_SIZE)
            for line in wrap(answer_to_str(results['founds'][found_idx])):
                yield head + line
                head = ' |'.ljust(LINE_HEAD_SIZE)
    yield ''
    if nb_unfound:
        yield ('A total of {} answer set{} expected but not found:'
               ''.format(nb_unfound, 's were' if nb_unfound > 1 else ' was'))
        for expecteds_idx in sorted(results['unfound']):
            source, solved, strict = results['expecteds'][expecteds_idx]
            for line in wrap(source.strip()):
                head = str(expecteds_idx) + ('s' if strict else ' ')
                yield head.ljust(LINE_HEAD_SIZE) + line.strip()
                head = ' |'.ljust(LINE_HEAD_SIZE)
            for line in wrap(answer_to_str(solved)):
                yield ' -->'.ljust(LINE_HEAD_SIZE) + line[:80].strip()
    yield ''
    if nb_overuse:
        yield ('A total of {} overused answer set{} found:'
               ''.format(nb_overuse, 's were' if nb_overuse > 1 else ' was'))
        for found_idx in sorted(results['invalid']):
            head = str(found_idx).ljust(LINE_HEAD_SIZE)
            yield head + answer_to_str(results['founds'][found_idx])
    yield ''


class ASPFile(pytest.File):
    def collect(self):
        """Get for each uid the source code to test, as an ASPItem"""
        block_by_uid = {}
        for uids, block, name in asp_parse_blocks(self.fspath.open(), self.fspath.purebasename):
            for uid in uids:
                block_by_uid.setdefault(uid, set()).add((tuple(block), name))
        test_case_by_uid = {}
        for uid, blocks in block_by_uid.items():
            test_case_by_uid[uid] = (
                (''.join(''.join(blo) for blo, _ in blocks)),
                (','.join(name for _, name in blocks)),
            )

        for uid, (source, name) in test_case_by_uid.items():
            name = name + '::' + uid
            yield ASPItem(self, source, uid, name, self.fspath.purebasename)


class ASPItem(pytest.Item):
    def __init__(self, parent, source, uid, name, fname):
        super().__init__(name, parent)
        self.source = ''.join(source)
        self.uid = uid
        self.fname = str(fname)
        self._test_case = None  # will be populated after collection (see hooks)

    @property
    def test_case(self): return self._test_case
    @test_case.setter
    def test_case(self, value):
        self._test_case = value

    def runtest(self):
        # print('RUNTEST:', self, self.test_case)
        if self.test_case is None:
            # print('SKIPPING:', self.test_case)
            pytest.skip(msg="No file for uid {}".format(self.uid))
        for inputcode, answers in self.test_case:
            result = verify_asp_code(inputcode + self.source, answers)
            # print('INPUTCODE, ANSWERS:', result)
            if not result['ok']:
                raise ASPException(self, result)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        # print('FAILURE:', excinfo, excinfo.value)
        if isinstance(excinfo.value, ASPException):
            return '\n'.join(repr_results(excinfo.value.args[1]))

    def reportinfo(self):
        return self.fspath, 0, "asptest: " + self.name
