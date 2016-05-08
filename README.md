# Littlewoods ID Verification

Django-based app that allows Littlewoods customers to upload documents proving
their identity. These documents are then sent to Littlewoods.

Then they get reviewed and customers whose identity was verified get Littlewoods
credits. Whoever, this project is not responsible for that functionality.

## Configuring AWS S3 bucket

The S3 bucket identified by the `S3_BUCKET` env var needs to have CORS enabled.

Note: CORS (Cross-Origin Resource Sharing) allows the user to upload his credentials
directly to S3, by-passing the django app. To do so, Javascript asks the Django app to
sign one URL per file to be uploaded. The Django app, using the AWS credentials,
creates those URLs and sends them back. Then Javascript, using the signed URLs, uploads
the files to S3.

CORS needs to be configured as follows:

    <?xml version="1.0" encoding="UTF-8"?>
    <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
        <CORSRule>
            <AllowedOrigin>*</AllowedOrigin>
            <AllowedMethod>GET</AllowedMethod>
            <AllowedMethod>PUT</AllowedMethod>
            <AllowedMethod>POST</AllowedMethod>
            <MaxAgeSeconds>3000</MaxAgeSeconds>
            <AllowedHeader>Authorization</AllowedHeader>
            <AllowedHeader>Content-Type</AllowedHeader>
            <AllowedHeader>*</AllowedHeader>
        </CORSRule>
    </CORSConfiguration>

## AWS User Policy for accessing the S3 bucket

The AWS user whose credentials (env vars `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`) are used
to upload/delete files to/from the S3 bucket needs to have the following AWS policy
applied:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1461353410000",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::lw-customer-verification-docs/*"
                ]
            }
        ]
    }

Make sure you use the appropriate "Resource" value.

## Local setup

    $ cp .env.sample .env
    $ docker-compose build
    $ docker-compose up

Make sure you properly initialize the vars in `.env`.
