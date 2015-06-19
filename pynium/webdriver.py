"""
Extend Selenium WebDriver classes to add useful methods.
"""

from selenium.common.exceptions import InvalidSelectorException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver, \
    WebElement

from selenium import webdriver

class EWebDriver(object):
    """
    Extended web driver mixin.
    """
    def create_web_element(self, element_id):
        return EWebElement(self, element_id)

    def find_elements_by_jquery(self, jq):
        return self.execute_script('return $(%r).get();' % jq)

    def find_element_by_jquery(self, jq):
        elems = self.find_elements_by_jquery(jq)
        if len(elems) == 1:
            return elems[0]
        else:
            raise InvalidSelectorException(
                "jQuery selector returned %i elements, expected 1" % len(elems)
            )


class EWebElement(WebElement):
    def find_elements_by_jquery(self, jq):
        return self.parent.execute_script(
            'return $(arguments[0]).find(%r).get();' % jq,
            self
        )

    def find_element_by_jquery(self, jq):
        elems = self.find_elements_by_jquery(jq)
        if len(elems) == 1:
            return elems[0]
        else:
            raise InvalidSelectorException(
                "jQuery selector returned %i elements, expected 1" % len(elems)
            )



_CLASSES = {}

def extended(driver_class):
    global _CLASSES

    if isinstance(driver_class, str):
        driver_class = getattr(webdriver, driver_class) 
    try:
        return _CLASSES[driver_class]
    except KeyError:
        pass
    # seems like concrete webdrivers are all subclass of RemoteWebDriver
    assert issubclass(driver_class, RemoteWebDriver)
    klass = type(driver_class.__name__, (EWebDriver, driver_class), {})
    _CLASSES[driver_class] = klass
    return klass
