import os
import pytest
from _pytest import junitxml
from collections import defaultdict
from pynium.webdriver import get_driver_factory, DriverFactory


def pytest_addoption(parser):
    parser.addoption("--webdriver", action="store", default='firefox',
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


class BrowserPool(object):
    def __init__(self):
        self.pool = defaultdict(dict)

    def register(self, browsername, parentid, browser):
        self.pool[browsername][parentid] = browser

    def get(self, browsername, parentid):
        if browsername not in self.pool:
            return None
        try:
            return self.pool[browsername][parentid]
        except KeyError:
            return None

    def clear(self):
        for k in self.pool.keys():
            for browser in self.pool[k].values():
                try:
                    browser.__factory__.quit(browser)
                except (IOError, OSError):
                    pass
        self.pool.clear()


@pytest.yield_fixture(scope='session')
def browser_pool(request):
    """
    Browser 'pool' to emulate session scope but with possibility to recreate
    browser.
    """
    pool = BrowserPool()
    yield pool
    pool.clear()


@pytest.fixture(scope='session')
def browser_instance_getter(session_scoped_browser, browser_pool):
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
    def get_browser(webdriver):
        factory = get_driver_factory(webdriver)
        return factory.create()

    def prepare_browser(request, parent, webdriver=None):
        webdriver = webdriver or request.config.option.webdriver
        parentid = id(parent)
        browser = browser_pool.get(webdriver, parentid)
        clear_browser = True
        if not session_scoped_browser:
            print('not session scoped')
            browser = get_browser(webdriver)
            request.addfinalizer(lambda: browser.__factory__.quit(browser))
            clear_browser = False
        elif not browser:
            if not webdriver in browser_pool.pool:
                print('cleaned')
                # we switched the browser, clear every other instances first
                browser_pool.clear()
            browser = get_browser(webdriver)
            browser_pool.register(webdriver, parentid, browser)
            clear_browser = False
        if clear_browser:
            # browser.manage().deleteAllCookies()
            browser.__factory__.clear(browser)
        return browser

    return prepare_browser


def pytest_generate_tests(metafunc):
    if 'browser' in metafunc.fixturenames:
        drivernames = metafunc.config.option.webdriver.split(',')
        if len(drivernames) <= 1:
            # do not paramtrize if we only have one dirver
            return
        scope = None
        if session_scoped_browser(metafunc):
            scope = "session"
        metafunc.parametrize("browser", drivernames, scope=scope,
                             indirect=True)


def pytest_funcarg__browser(request, browser_instance_getter):
    drivername = getattr(request, 'param', None)
    return browser_instance_getter(request, pytest_generate_tests, drivername)


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
        if isinstance(getattr(value, '__factory__', None), DriverFactory):
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
                browser.__factory__.save_screenshot(browser, screenshot_path)
            except Exception as e:
                request.config.warn(
                    'SPL504', "Could not save screenshot: %s" % e
                )
