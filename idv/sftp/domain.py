import base64
import contextlib
import errno
import logging

import paramiko

from .proxy import http as http_proxy_util

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def sftp_client_from_model(sftp_account, http_proxy):
    client = get_sftp_client_from_model(sftp_account, http_proxy)
    yield client
    client.sock.transport.close()


def get_sftp_client_from_model(sftp_account, http_proxy=None):
    """
    Instantiate SFTP client from a SftpAccount model.

    Returns:
        paramiko.SFTPClient: connected to the host
    """
    sock = get_transport_sock(sftp_account, http_proxy)
    transport = paramiko.Transport(sock)
    transport.start_client()

    server_key = transport.get_remote_server_key()
    if not sftp_account.host_key_data:
        store_host_key_data(sftp_account, server_key)
        logger.info('Stored key data for for host %s.', sftp_account.host)
    else:
        ensure_host_key_matches(sftp_account, server_key)

    transport.auth_password(sftp_account.username, sftp_account.password)
    return paramiko.SFTPClient.from_transport(transport)


def get_transport_sock(sftp_account, http_proxy=None):
    if http_proxy:
        host, port = sftp_account.host, sftp_account.port
        return http_proxy_util.get_tunneled_sock(host, port, http_proxy)
    else:
        return (sftp_account.host, sftp_account.port)


def store_host_key_data(sftp_account, server_key):
    key_type = server_key.get_name()
    sftp_account.host_key_type = key_type
    sftp_account.host_key_data = server_key.get_base64()
    sftp_account.save()


def ensure_host_key_matches(sftp_account, server_key):
    key_type = server_key.get_name()
    key_data = base64.b64decode(server_key.get_base64())
    key_fprint = get_key_fingerprint(server_key)

    if (
        sftp_account.host_key_type != key_type or
        sftp_account.host_key_data_binary != key_data
    ):
        raise SftpClientException(
            'WARNING: Remote host identification has changed! Host {host} '
            'provided {new_key_type} key: {new_key_fingerprint}, '
            'expected {old_key_type} key: {old_key_fingerprint}'
            .format(host=sftp_account.host,
                    new_key_type=key_type,
                    new_key_fingerprint=key_fprint,
                    old_key_type=sftp_account.host_key_type,
                    old_key_fingerprint=sftp_account.host_key_fingerprint))


class SftpClientException(Exception):
    pass


def get_key_fingerprint(key):
    data = key.get_fingerprint()
    return ':'.join(format(x, '02x') for x in bytearray(data))


def path_exists(sftp_client, path):
    try:
        sftp_client.stat(path)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return False
        raise
    return True
