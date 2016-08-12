from enum import Enum, unique


@unique
class CredentialStatus(Enum):
    """
    Its members represent all possible statuses an
    `idv.collector.models.Credential` object can have.
    """
    # The user requested permission for uploding the file to S3
    # but we don't know yet if it was uploaded successfully.
    Unchecked = 0
    # We confirm that the file was found in S3.
    Found = 1
    # We tried to fetch the file from S3 but it wasn't there.
    # This may happen for example if the user disconnects while uploading
    # the file.
    NotFound = 2
    # The file has been copied to the LW sftp server.
    Copied = 3
    # The file has been copied to LW Sftp and deleted from FW S3.
    Moved = 4
    # Files with non-whitelisted extensions are blocked and remain on S3
    # for further inspection.
    Blocked = 5
