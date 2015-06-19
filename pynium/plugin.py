from pynium import webdriver
import pytest


def pytest_addoption(parser):
    parser.addoption("--driver", action="store", default='Firefox',
                     help="Web driver to use, default to %(default)s")


@pytest.yield_fixture(scope='session')
def driver(request):
    browser_class = webdriver.extended(request.config.getoption("--driver"))
    browser = browser_class()
    yield browser
    browser.quit()
