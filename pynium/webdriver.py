"""
Extend Selenium WebDriver classes to add useful methods.
"""

from selenium.common.exceptions import InvalidSelectorException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver, \
    WebElement

from selenium.webdriver import Firefox, Chrome, Ie, Opera, Safari, \
    BlackBerry, PhantomJS, Android

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


class firefox(EWebDriver, Firefox):
    pass


class chrome(EWebDriver, Chrome):
    pass


class ie(EWebDriver, Ie):
    pass


class opera(EWebDriver, Opera):
    pass


class safari(EWebDriver, Safari):
    pass


class blackberry(EWebDriver, BlackBerry):
    pass


class phantomjs(EWebDriver, PhantomJS):
    pass


class android(EWebDriver, Android):
    pass


class remote(EWebDriver, RemoteWebDriver):
    pass


_CLASSES = dict(firefox=firefox, chrome=chrome, ie=ie, opera=opera,
                safari=safari, blackberry=blackberry, phantomjs=phantomjs,
                android=android, remote=remote)

def get_driver_class(name):
    return _CLASSES[name]
