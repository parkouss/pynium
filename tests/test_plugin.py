import inspect
import os


def test_simple_page(browser, http_server):
    browser.get(http_server)
    assert os.path.basename(inspect.getsourcefile(test_simple_page)) \
        in browser.page_source
