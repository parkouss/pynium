from selenium.webdriver.common.keys import Keys


def test_one(driver):
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source


def test_two(driver):
    # logic extracted from code generation using
    # firefox selenium plugin:
    # http://www.seleniumhq.org/download/
    driver.get("http://try.jquery.com/")
    driver.find_element_by_css_selector("b").click()
    assert driver.find_element_by_link_text("What is jQuery?") is not None
