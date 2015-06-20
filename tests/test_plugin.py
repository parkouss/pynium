import os
import py
import pytest


@pytest.yield_fixture
def testit(request, testdir, http_server, tests_dir, default_drivers):
    testdir.makeconftest(open(os.path.join(tests_dir, 'conftest.py')).read())
    testdir.base_url = http_server

    def _runp_default(*args, **kwargs):
        args = args + ('--webdriver', default_drivers[0])
        return testdir.runpytest(*args, **kwargs)

    def _run_all(*args, **kwargs):
        args = args + ('--webdriver', ','.join(default_drivers))
        return testdir.runpytest(*args, **kwargs)

    testdir.runpytest_in_default_browser = _runp_default
    testdir.runpytest_in_all_browsers = _run_all
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
    result = testit.runpytest_in_default_browser()
    assert result.parseoutcomes().get('passed') == 1


def test_error_should_take_screenshot(testit):
    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest_in_default_browser()
    assert result.parseoutcomes().get('failed') == 1
    assert testit.tmpdir.join("test_error_should_take_screenshot",
                              "test_simple_page-browser.png").exists()


def test_error_should_not_take_screenshot_if_specified(testit):
    testit.makepyfile(py.code.Source(r"""
        def test_simple_page(browser):
            browser.get(%r)
            elem = browser.find_element_by_id("thisdoesnotexist")
""" % (testit.base_url + '/simple.html')))
    result = testit.runpytest_in_default_browser(
        '--make-screenshot-on-failure=false'
    )
    assert result.parseoutcomes().get('failed') == 1
    assert not testit.tmpdir.join("test_error_should_take_screenshot",
                                  "test_simple_page-browser.png").exists()


def test_one_browser_by_test_session(testit):
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
""" % (testit.base_url + '/simple.html')))
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


def test_multiple_browser(testit, default_drivers):
    testit.makepyfile(py.code.Source(r"""
        import pytest
        BROWSERS = []

        def test1(browser):
            assert browser not in BROWSERS
            BROWSERS.append(browser)

        def test2(browser):
            assert browser in BROWSERS

        def test3(browser):
            assert browser in BROWSERS
"""))
    result = testit.runpytest_in_all_browsers('-v')
    assert result.parseoutcomes().get('passed') == \
        len(default_drivers) * 3

    expected = []
    for drivername in default_drivers:
        for func in ('test1', 'test2', 'test3'):
            expected.append(
                'test_multiple_browser.py::%s[%s] PASSED' % (func, drivername)
            )
    assert [l for l in result.stdout.lines if l.endswith('PASSED')] == expected


def test_multiple_browser_no_session_scoped(testit, default_drivers):
    testit.makepyfile(py.code.Source(r"""
        import pytest
        BROWSERS = []

        def test1(browser):
            assert browser not in BROWSERS
            BROWSERS.append(browser)

        def test2(browser):
            assert browser not in BROWSERS
            BROWSERS.append(browser)

        def test3(browser):
            assert browser not in BROWSERS
            BROWSERS.append(browser)
"""))
    result = testit.runpytest_in_all_browsers(
        '-v', '--session-scoped-browser=false'
    )
    assert result.parseoutcomes().get('passed') == \
        len(default_drivers) * 3

    expected = []
    for func in ('test1', 'test2', 'test3'):
        for drivername in default_drivers:
            expected.append(
                'test_multiple_browser_no_session_scoped.py::%s[%s] PASSED'
                % (func, drivername)
            )
    assert [l for l in result.stdout.lines if l.endswith('PASSED')] == expected
