import base64
import contextlib
import logging

import paramiko

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def get_sftp_client_from_model(cfg, create_host_key=True):
    client = _get_sftp_client_from_model(cfg, create_host_key=create_host_key)
    yield client
    client.sock.transport.close()


def _get_sftp_client_from_model(cfg, create_host_key=True):
    """Instantiate SFTP client from a SftpAccount model.

    Args:
        create_host_key: if True (the default) the host key will be
            stored if this was the first time connecting to the host;
            otherwise, an exception will be raised.

    Returns:
        paramiko.SFTPClient: connected to the host
    """
    transport = paramiko.Transport((cfg.host, cfg.port))
    transport.start_client()

    server_key = transport.get_remote_server_key()

    key_type = server_key.get_name()
    key_data = base64.b64decode(server_key.get_base64())
    key_fprint = get_key_fingerprint(server_key)

    if not cfg.host_key_data:
        if not create_host_key:
            raise SftpClientException(
                'No host key specified for host {host}, yet '
                'create_host_key=False was specified. '
                'Provided key is {key_type}: {key_fingerprint}'
                .format(host=cfg.host,
                        key_type=key_type,
                        key_fingerprint=key_fprint))

        logger.info(
            'This is the first time we connect to %(host)s. '
            'Storing %(key_type)s key %(key_fingerprint)s.',
            dict(host=cfg.host, key_type=key_type, key_fingerprint=key_fprint))

        cfg.host_key_type = key_type
        cfg.host_key_data = server_key.get_base64()
        cfg.save()

    else:
        # Ensure that the host key matches
        if (cfg.host_key_type != key_type or
                cfg.host_key_data_binary != key_data):

            raise SftpClientException(
                'WARNING: Remote host identification has changed! Host {host} '
                'provided {new_key_type} key: {new_key_fingerprint}, '
                'expected {old_key_type} key: {old_key_fingerprint}'
                .format(host=cfg.host,
                        new_key_type=key_type,
                        new_key_fingerprint=key_fprint,
                        old_key_type=cfg.host_key_type,
                        old_key_fingerprint=cfg.host_key_fingerprint))

    transport.auth_password(cfg.username, cfg.password)
    return paramiko.SFTPClient.from_transport(transport)


class SftpClientException(Exception):
    pass


def get_key_fingerprint(key):
    data = key.get_fingerprint()
    return ':'.join(format(x, '02x') for x in bytearray(data))
