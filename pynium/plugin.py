from pynium.webdriver import extended as extended_webdriver
import pytest


def pytest_addoption(parser):
    parser.addoption("--webdriver", action="store", default='Firefox',
                     help="Web driver to use, default to %(default)s")


@pytest.fixture(scope='session')
def webdriver(request):
    """
    webdriver name fixture.
    """
    return request.config.option.webdriver


@pytest.yield_fixture(scope='session')
def browser(webdriver):
    browser_class = extended_webdriver(webdriver)
    browser = browser_class()
    yield browser
    browser.quit()
