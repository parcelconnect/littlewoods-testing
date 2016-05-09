import base64
import hashlib

from django.db import models


CHARFIELD_SAFE_LIMIT = 1024
SFTP_DEFAULT_PORT = 22


class SFTPAccount(models.Model):

    host = models.CharField(max_length=CHARFIELD_SAFE_LIMIT)
    port = models.IntegerField(default=SFTP_DEFAULT_PORT)
    username = models.CharField(max_length=CHARFIELD_SAFE_LIMIT)
    password = models.CharField(max_length=CHARFIELD_SAFE_LIMIT)
    base_path = models.CharField(max_length=CHARFIELD_SAFE_LIMIT)

    # Used for key verification.
    # They will be automatically populated on first connection to the server.
    # In case of "host key mismatch" exceptions, those fields can be blanked
    # in order to update host key information.
    host_key_type = models.CharField(
        max_length=CHARFIELD_SAFE_LIMIT,
        blank=True, null=True
    )
    host_key_data = models.CharField(
        max_length=CHARFIELD_SAFE_LIMIT,
        blank=True, null=True
    )

    url_schema = 'sftp://'

    @property
    def host_key_data_binary(self):
        return base64.b64decode(self.host_key_data)

    @host_key_data_binary.setter
    def host_key_data_binary(self, data):
        self.host_key_data = base64.b64decode(data)

    def host_key_fingerprint(self):
        data = self.host_key_data_binary
        fingerprint = hashlib.md5(data).digest()
        return ':'.join(format(x, '02x') for x in bytearray(fingerprint))

    def __str__(self):
        return '{}{}@{}:{}'.format(
            self.url_schema,
            self.username,
            self.host,
            self.port
        )
