import os
import pytest
from _pytest import junitxml
from pynium.webdriver import extended as extended_webdriver, EWebDriver


def pytest_addoption(parser):
    parser.addoption("--webdriver", action="store", default='Firefox',
                     help="Web driver to use, default to %(default)s")
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


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    """
    Assign the report to the item for futher usage.
    """
    rep = __multicall__.execute()
    if rep.outcome != 'passed':
        item.selenium_failure = rep
    else:
        item.selenium_failure = None
    return rep


@pytest.yield_fixture(autouse=True)
def browser_screenshot(request, screenshot_dir, make_screenshot_on_failure):
    """
    Make browser screenshot on test failure.
    """
    yield
    if not (make_screenshot_on_failure and request.node.selenium_failure):
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


@pytest.yield_fixture(scope='session')
def browser(webdriver):
    browser_class = extended_webdriver(webdriver)
    browser = browser_class()
    yield browser
    browser.quit()
