import os
import py
import pytest


@pytest.fixture
def testit(request, testdir, tests_dir, webdriver, webdriver_executable):
    testdir.makeconftest(open(os.path.join(tests_dir, 'conftest.py')).read())

    dargs = ('--webdriver-executable=%s' % (webdriver_executable or ''),)

    def _runp_default(*args, **kwargs):
        args = args + dargs + ('--webdriver', webdriver)
        return testdir.runpytest(*args, **kwargs)

    testdir.runpytest_in_default_browser = _runp_default
    return testdir


def test_simple_page(testit, http_server):
    http_server.serve_local_file('simple.html')

    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_tag_name("h1")
            assert elem.text == 'My First Heading'
""" % http_server.url))
    result = testit.runpytest_in_default_browser()
    assert result.parseoutcomes().get('passed') == 1


@pytest.mark.skipif(os.name == 'nt',
                    reason="requires investigation")
def test_error_should_take_screenshot(testit, http_server):
    http_server.serve_local_file('simple.html')

    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % http_server.url))
    result = testit.runpytest_in_default_browser()
    assert result.parseoutcomes().get('failed') == 1
    assert testit.tmpdir.join("test_error_should_take_screenshot",
                              "test_simple_page-browser.png").exists()


def test_error_should_not_take_screenshot_if_specified(testit, http_server):
    http_server.serve_local_file('simple.html')

    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % http_server.url))
    result = testit.runpytest_in_default_browser(
        '--make-screenshot-on-failure=false'
    )
    assert result.parseoutcomes().get('failed') == 1
    assert not testit.tmpdir.join("test_error_should_take_screenshot",
                                  "test_simple_page-browser.png").exists()


def test_one_browser_by_test_session(testit, http_server):
    http_server.serve_local_file('simple.html')

    testit.makepyfile(py.code.Source(r"""
        import pytest
        USED_BROWSER = None

        def test_first(browser):
            global USED_BROWSER
            browser.get(%r)
            USED_BROWSER = browser

        def test_second(browser):
            browser.current_url == 'about:blank'
            assert USED_BROWSER == browser
""" % http_server.url))
    result = testit.runpytest_in_default_browser()
    assert result.parseoutcomes().get('passed') == 2


def test_one_browser_by_test_if_specified(testit):
    testit.makepyfile(py.code.Source(r"""
        import pytest
        USED_BROWSER = None

        def test_first(browser):
            global USED_BROWSER
            USED_BROWSER = browser

        def test_second(browser):
            assert USED_BROWSER != browser
"""))
    result = testit.runpytest_in_default_browser(
        '--session-scoped-browser=false'
    )
    assert result.parseoutcomes().get('passed') == 2
