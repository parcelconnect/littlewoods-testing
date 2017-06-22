# Repo description

Every now and then, Littlewoods asks for a new small, stand-alone app. Instead of having
multiple repositories for these, we keep them all together under this repo.

- - -

# App: Littlewoods ID Verification

Django-based app that allows Littlewoods customers to upload documents proving
their identity. These documents are then sent to Littlewoods.

Then they get reviewed and customers whose identity was verified get Littlewoods
credits. Whoever, this project is not responsible for that functionality.

## Django apps used

- collector
- mover
- sftp

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
            },
            {
                "Sid": "Stmt1461353410001",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::lw-customer-verification-docs"
                ]
            }
        ]
    }

Make sure you use the appropriate "Resource" value.

## Local setup

Create an empty `.env` file.

    $ docker-compose build
    $ docker-compose up

## EC2 proxy for copying files from Fastway S3 to LW SFTP

To allow us upload files to their SFTP server, Littlewoods wanted to whitelist
our IP, that is the IP of the Django App Server:

Fastway S3 --->--- Django App Server -->--- LW SFTP

However, our app runs on heroku and we could not provide such an IP.
To solve the issue, we use an EC2 proxy associated with an Elastic IP:

Fastway S3 -->--> Django App Server -->-- EC2 HTTP PROXY -->-- LW SFTP

The EC2 proxy instance runs an HTTP proxy called Tinyproxy (tinyproxy.github.io).
The App, using an HTTP Connect request, asks the HTTP proxy to forward the
original SFTP request to LW SFTP.

That EC2 instance is under the `parcelconnect` AWS account and it's named
`fastwaybox`.

The url for AWS management console access is: https://fastway-ie.signin.aws.amazon.com/console
(as of this edit, there are users in IAM defined for salvadorperez, miqueltorres and pcurtain)

- - -

# App: Tracking

A Littlewoods-whitelabeled page for tracking fastway consignments. Tracking info is fetched by hitting the Global API.

## Django apps used

- tracker

- - -

# App: Gift wrapping

As Littlewoods could not invest man power to add a 'wrap as a gift' checkbox on their webpage, this app does exactly that. After an order is made on Littlewoods, the customer can click on a link, be transferred in here, provide his order details and get his parcel wrapped.

## Django apps used

- giftwrap
