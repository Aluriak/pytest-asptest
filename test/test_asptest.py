# -*- coding: utf-8 -*-


def test_bar_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makefile('hadoken.lp', """
% TEST: data-generation, two-in-one
p(1..3).

% TEST qrule: rule-q, two-in-one
q(X): p(X).
    """)

    # # run pytest with the following cmd args
    result = testdir.runpytest(
        '-p asptest',
        '--uid-tests-dir=examples',
        '-v'
    )

    # # fnmatch_lines does an assertion internally
    print(result.stdout.lines)
    result.stdout.fnmatch_lines([
        '*::test_block* PASSED*',
    ])

    # # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


# def test_help_message(testdir):
    # result = testdir.runpytest(
        # '--help',
    # )
    # # fnmatch_lines does an assertion internally
    # result.stdout.fnmatch_lines([
        # 'asptest:',
        # '*--uid-tests-dir=examples*Set the value for the fixture "bar".',
    # ])
