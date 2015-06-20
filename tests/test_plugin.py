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
    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_tag_name("h1")
            assert elem.text == 'My First Heading'
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest()
    assert result.parseoutcomes().get('passed') == 1


def test_error_should_take_screenshot(testit):
    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest()
    assert result.parseoutcomes().get('failed') == 1
    assert testit.tmpdir.join("test_error_should_take_screenshot",
                              "test_simple_page-browser.png").exists()


def test_error_should_not_take_screenshot_if_specified(testit):
    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest('--make-screenshot-on-failure=false')
    assert result.parseoutcomes().get('failed') == 1
    assert not testit.tmpdir.join("test_error_should_take_screenshot",
                                  "test_simple_page-browser.png").exists()


def test_one_browser_by_test_session(testit):
    testit.makepyfile(py.code.Source(r"""
        import pytest
        USED_BROWSER = None
        @pytest.mark.run(order=1)
        def test_first(browser):
            global USED_BROWSER
            browser.get(%r)
            USED_BROWSER = browser
        @pytest.mark.run(order=2)
        def test_second(browser):
            browser.current_url == 'about:blank'
            assert USED_BROWSER == browser
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest()
    assert result.parseoutcomes().get('passed') == 2


def test_one_browser_by_test_if_specified(testit):
    testit.makepyfile(py.code.Source(r"""
        import pytest
        USED_BROWSER = None
        @pytest.mark.run(order=1)
        def test_first(browser):
            global USED_BROWSER
            USED_BROWSER = browser
        @pytest.mark.run(order=2)
        def test_second(browser):
            assert USED_BROWSER != browser
"""))
    result = testit.runpytest('--session-scoped-browser=false')
    assert result.parseoutcomes().get('passed') == 2
