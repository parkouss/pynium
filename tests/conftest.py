import os
import pytest


pytest_plugins = 'pytester'


@pytest.fixture(scope='session')
def tests_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope='session')
def http_root_dir(tests_dir):
    return os.path.join(tests_dir, 'http_root')


@pytest.fixture()
def http_server(httpserver, http_root_dir):
    def serve_local_file(fname):
        with open(os.path.join(http_root_dir, fname)) as f:
            httpserver.serve_content(f.read())
    httpserver.serve_local_file = serve_local_file
    return httpserver
