import os
import pytest
from multiprocessing import Process, Pipe


pytest_plugins = 'pytester'


def run_server(conn, http_root_dir):
    from six.moves import SimpleHTTPServer
    from six.moves import socketserver
    os.chdir(http_root_dir)
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.socket.getsockname()[1]
    print("http://127.0.0.1:%d" % port)
    conn.send("http://127.0.0.1:%d" % port)
    httpd.serve_forever()


@pytest.fixture(scope='session')
def tests_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope='session')
def http_root_dir(tests_dir):
    return os.path.join(tests_dir, 'http_root')


@pytest.yield_fixture(scope='session')
def http_server(http_root_dir):
    parent_conn, child_conn = Pipe()
    p = Process(target=run_server, args=(child_conn, http_root_dir))
    p.start()
    base_url = parent_conn.recv()
    yield base_url
    p.terminate()
    p.join()


@pytest.fixture(scope='session')
def default_drivers():
    return ('phantomjs', 'firefox')
