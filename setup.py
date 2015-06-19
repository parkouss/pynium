
from setuptools import setup

setup(
    name="pynium",
    version='0.0.1',
    packages=['pynium'],
    entry_points={
        'pytest11': ['pytest-selenium = pynium.plugin'],
    },
    install_requires=['pytest>=2.7.0', 'selenium'],
    author=u"Julien Pagès",
    author_email="j.parkouss@gmail.com",
    description='pytest support for selenium testing',
)
