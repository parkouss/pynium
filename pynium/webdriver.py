"""
Extend Selenium WebDriver classes to add useful methods.
"""

from selenium.common.exceptions import InvalidSelectorException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver, \
    WebElement

from selenium.webdriver import Firefox, Chrome, Ie, Opera, Safari, \
    BlackBerry, PhantomJS, Android


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


class DriverFactory(object):
    def __init__(self, driver_class):
        self.driver_class = driver_class

    def _create(self, *args, **kwargs):
        return self.driver_class(*args, **kwargs)

    def create(self, *args, **kwargs):
        instance = self._create(*args, **kwargs)
        instance.__factory__ = self
        return instance

    def clear(self, instance):
        # naive implementation
        instance.get('about:blank')

    def save_screenshot(self, instance, screenshot_path):
        instance.save_screenshot(screenshot_path)

    def quit(self, instance):
        instance.quit()


_factories = {}


def get_driver_factory(name):
    return _factories[name]


def register_driver_factory(name, factory):
    _factories[name] = factory


for klass in (firefox, chrome, ie, opera, safari, blackberry, phantomjs,
              android, remote):
    register_driver_factory(klass.__name__, DriverFactory(klass))
