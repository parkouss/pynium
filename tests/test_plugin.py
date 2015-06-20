import os
import py
import pytest


@pytest.yield_fixture
def testit(request, testdir, http_server, tests_dir):
    testdir.makeconftest(open(os.path.join(tests_dir, 'conftest.py')).read())
    testdir.base_url = http_server
    yield testdir
    # remove testdir
    request.config._tmpdirhandler.getbasetemp().remove()


def test_simple_page(testit):
    recorder = testit.inline_runsource(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_tag_name("h1")
            assert elem.text == 'My First Heading'
""" % (testit.base_url + '/simple.html')))
    recorder.assertoutcome(passed=1)
