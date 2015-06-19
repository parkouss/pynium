from selenium.webdriver.common.keys import Keys


def test_one(browser):
    browser.get("http://www.python.org")
    assert "Python" in browser.title
    elem = browser.find_element_by_name("q")
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in browser.page_source


def test_two(browser):
    # logic extracted from code generation using
    # firefox selenium plugin:
    # http://www.seleniumhq.org/download/
    browser.get("http://try.jquery.com/")
    browser.find_element_by_css_selector("b").click()
    assert browser.find_element_by_link_text("What is jQuery?") is not None
