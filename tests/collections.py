from __future__ import with_statement

import sys

from attest import AbstractReporter, Tests, Assert, capture_output


class Failure(object):

    def __init__(self, test, error, traceback, stdout, stderr):
        self.test = Assert(test)
        self.error = Assert(error)
        self.traceback = Assert(traceback)
        self.stdout = Assert(stdout)
        self.stderr = Assert(stderr)


class TestReporter(AbstractReporter):

    def begin(self, tests):
        self.succeeded = []
        self.failed = []

    def success(self, test, stdout, stderr):
        self.succeeded.append(Assert(test))

    def failure(self, test, error, traceback, stdout, stderr):
        self.failed.append(Failure(test, error, traceback, stdout, stderr))

    def finished(self):
        pass


suite = Tests()


@suite.test
def decorator():
    """@Tests().test"""

    col = Tests()

    @col.test
    def one(): pass

    @col.test
    def two(): pass

    Assert(len(col)) == 2
    Assert(list(col)) == [one, two]


@suite.test
def context():
    """@Tests().context"""

    col = Tests()

    @col.test
    def test(calculated):
        Assert(calculated) == 2

    @col.context
    def context():
        calculated = 1 + 1
        yield calculated

    @col.test
    def noctx():
        pass

    test()
    noctx()

    col2 = Tests()

    @col2.context
    def empty():
        yield

    @col2.test
    def test2():
        pass

    test2()

    col3 = Tests()

    @col3.context
    def multiple():
        yield 1, 2, 3

    @col3.test
    def test3(one, two, three):
        Assert(one) == 1
        Assert(two) == 2
        Assert(three) == 3

    test3()

    col4 = Tests()

    @col4.context
    def nested():
        yield 1

    @col4.context
    def nested():
        yield

    @col4.context
    def nested():
        yield 2

    @col4.test
    def test4(one, two):
        Assert(one) == 1
        Assert(two) == 2

    test4()


@suite.test
def capture():
    """capture_output()"""

    stdout, stderr = sys.stdout, sys.stderr

    with capture_output() as (out, err):
        print 'Capture the flag!'
        print >>sys.stderr, 'Rapture the flag?'

    Assert(out) == ['Capture the flag!']
    Assert(err) == ['Rapture the flag?']

    Assert(sys.stdout).is_(stdout)
    Assert(sys.stderr).is_(stderr)


@suite.test
def run():
    """Tests().run"""

    col = Tests()

    @col.test
    def fail():
        Assert(1) == 2

    @col.test
    def succeed():
        Assert(1) == 1

    @col.test
    def exit():
        raise SystemExit

    result = TestReporter()
    with Assert.not_raising(SystemExit):
        col.run(result)

    Assert(len(result.failed)) == 2
    Assert(len(result.succeeded)) == 1

    result.failed[0].test.is_(fail)
    result.failed[0].error.__class__.is_(AssertionError)
    result.succeeded[0].is_(succeed)
