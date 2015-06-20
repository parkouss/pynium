import os
import pytest
from _pytest import junitxml
from pynium.webdriver import extended as extended_webdriver, EWebDriver


def pytest_addoption(parser):
    parser.addoption("--webdriver", action="store", default='Firefox',
                     help="Web driver to use, default to %(default)s")
    parser.addoption("--session-scoped-browser",
                     help="should use a single browser instance per test"
                     " session. Defaults to true.", action="store",
                     metavar="false|true", type="choice",
                     choices=('false', 'true'), default='true')
    parser.addoption('--make-screenshot-on-failure', default='true',
                     help="should take browser screenshots on test failure."
                     " Defaults to true.",
                     action='store', metavar="false|true", type="choice",
                     choices=('false', 'true'))
    parser.addoption("--screenshot-dir",
                     help="browser screenshot directory."
                     " Defaults to the current directory.", action="store",
                     metavar="DIR", default='.')


@pytest.fixture(scope='session')
def webdriver(request):
    """
    webdriver name fixture.
    """
    return request.config.option.webdriver


@pytest.fixture(scope='session')
def make_screenshot_on_failure(request):
    """
    Flag to make browser screenshot on test failure.
    """
    return request.config.option.make_screenshot_on_failure == 'true'


@pytest.fixture(scope='session')
def screenshot_dir(request):
    """
    Browser screenshot directory.
    """
    return os.path.abspath(request.config.option.screenshot_dir)


@pytest.fixture(scope='session')
def session_scoped_browser(request):
    """
    Flag to keep single browser per test session.
    """
    return request.config.option.session_scoped_browser == 'true'


@pytest.yield_fixture(scope='session')
def browser_pool(request):
    """
    Browser 'pool' to emulate session scope but with possibility to recreate
    browser.
    """
    pool = {}
    yield pool
    for browser in pool.values():
        try:
            browser.quit()
        except (IOError, OSError):
            pass


@pytest.fixture(scope='session')
def browser_instance_getter(session_scoped_browser, webdriver, browser_pool):
    """
    Function to create an instance of the browser.

    This fixture is required only if you need to have multiple instances of
    the Browser in a single test at the same time. Example of usage: ::

      @pytest.fixture
      def admin_browser(request, browser_instance_getter):
          '''Admin browser fixture.'''
          # browser_instance_getter function receives parent fixture
          # -- our admin_browser
          return browser_instance_getter(request, admin_browser)

      def test_2_browsers(browser, admin_browser):
          '''Test using 2 browsers at the same time.'''
          browser.get('http://google.com')
          admin_browser.get('http://admin.example.com')
    """
    def get_browser():
        browser_class = extended_webdriver(webdriver)
        return browser_class()

    def prepare_browser(request, parent):
        browser_key = id(parent)
        browser = browser_pool.get(browser_key)
        clear_browser = True
        if not session_scoped_browser:
            browser = get_browser()
            request.addfinalizer(browser.quit)
            clear_browser = False
        elif not browser:
            browser = browser_pool[browser_key] = get_browser()
            clear_browser = False
        if clear_browser:
            # browser.manage().deleteAllCookies()
            browser.get('about:blank')
        return browser

    return prepare_browser


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    """
    Assign the report to the item for futher usage.
    """
    rep = __multicall__.execute()
    if rep.outcome != 'passed':
        item.selenium_failure = rep
    return rep


@pytest.yield_fixture(autouse=True)
def browser_screenshot(request, screenshot_dir, make_screenshot_on_failure):
    """
    Make browser screenshot on test failure.
    """
    yield
    if not (make_screenshot_on_failure and
            getattr(request.node, 'selenium_failure', None)):
        return
    for name, value in request._funcargs.items():
        # find instance of webdriver in function args
        if isinstance(value, EWebDriver):
            browser = value
            names = junitxml.mangle_testnames(request.node.nodeid.split("::"))
            classname = '.'.join(names[:-1])
            screenshot_dir = os.path.join(screenshot_dir, classname)
            screenshot_file_name = '{0}-{1}.png'.format(
                names[-1][:128 - len(name) - 5], name
            )
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            screenshot_path = \
                os.path.join(screenshot_dir, screenshot_file_name)
            try:
                browser.save_screenshot(screenshot_path)
            except Exception as e:
                request.config.warn(
                    'SPL504', "Could not save screenshot: %s" % e
                )


@pytest.fixture
def browser(request, browser_instance_getter):
    """
    Browser fixture.
    """
    return browser_instance_getter(request, browser)
