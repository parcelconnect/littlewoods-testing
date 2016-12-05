import base64
from collections import namedtuple
from http.client import HTTPConnection

HttpProxy = namedtuple('HttpProxy', ['host', 'port', 'username', 'password'])


def get_tunneled_connection(host, port, proxy):
    headers = {}
    if proxy.username and proxy.password:
        headers['Proxy-Authorization'] = get_proxy_auth_header(proxy)

    connection = HTTPConnection(proxy.host, proxy.port)
    connection.set_tunnel(host, port, headers)
    connection.connect()

    return connection


def get_proxy_auth_header(proxy):
    auth = '{}:{}'.format(proxy.username, proxy.password)
    base64auth = base64.b64encode(auth.encode('ascii')).decode()
    proxy_authorization_header = 'Basic ' + base64auth
    return proxy_authorization_header


def get_tunneled_sock(host, port, proxy):
    connection = get_tunneled_connection(host, port, proxy)
    return connection.sock
