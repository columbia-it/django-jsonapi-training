"""
This file and zappa_settings.json are part of demo configurations of running the Django-training application
as AWS Lambda function by using Zappa (https://github.com/Miserlou/Zappa).

This file is dealing with two things: db credentials and Django static files.

There are many ways to store/retrieve db credentials under AWS environment.
Here it shows 4 different simple ways to do this.

Method 1 - Using Zappa remote_env
1) To encrypt the value of db, user and password etc one by one as:
https://docs.aws.amazon.com/cli/latest/reference/kms/encrypt.html or
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.encrypt.
2) Put the output of AWS KMS encryption into a file as the JSON format as
{"DJANGO_MYSQLSERVER_DB": "value from above", ...}.
3) Place that JSON file into S3.
4) Add "remote_env": "s3://your-bucket/your-file" into your zappa JSON file, thus Zappa will load it for you.


Method 2 - Using Zappa local environment_variables
"environment_variables": {"your_key": "your_aws_kms_encrypted_value"}
This probably is the simplest way to pass around the db credentials.


Method 3 - Method 1's alternative way
1) Put the original value into a json file as: { "DJANGO_MYSQLSEVER_D", "...", ...}
2) To encrypt the file as above reference links.
3) Put your encrypted file into s3.
When cp file to bucket, you can use either way as bellow:
aws s3 cp ./my_file s3://my_bucket/ --sse aws:kms
or
aws s3 cp ./my_file s3://my_bucket/ --sse aws:kms --sse-kms-key-id my_key
References:
https://aws.amazon.com/premiumsupport/knowledge-center/s3-object-encrpytion-keys/
https://docs.aws.amazon.com/AmazonS3/latest/dev/serv-side-encryption.html
https://docs.aws.amazon.com/kms/latest/developerguide/services-s3.html
In this way,  you can't use remote_env of zappa, meaning to retrieve it from s3 by yourself.


Method 4 - Using AWS Secrets Manager
1) You can use either aws console, aws-cli, boto3 or template yaml(see an example in ..aws/rds folder)
to create and store a secret.  Using aws-cli or boto3 to create the secret will be easier than console
if you want to have customer key and/or SecretBinary formatting etc.
Please refer to AWS documentation for details:
https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/create-secret.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
2) Create a new managed policy
https://docs.aws.amazon.com/cli/latest/reference/iam/create-policy.html
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "secretsmanager:GetSecretValue",
        "Resource": "<arn-from-above-step-1>"
    }
}
3) Attach the policy with this lambda role
https://docs.aws.amazon.com/cli/latest/reference/iam/attach-role-policy.html
Step 2) and 3) may be replaced by { ... "attach_policy": "my_attach_policy.json"...} or extra_permissions etc
in zappa_settings.json. Please refer to Zappa doc for details if you want to do in the zappa way.
{
    ...
    "manage_roles": true,
    "extra_permissions": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "<arn-of-your-app-needs-to-access>"
        }
    ],
    ...
}


Method 5 - Using AWS SSM Parameter Store
Reference:
https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
https://docs.aws.amazon.com/cli/latest/reference/ssm/put-parameter.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter
We will put this method in here next time.


For hosting Django static files - https://romandc.com/zappa-django-guide/walk_static/

The vpc config can be set up either in the zappa_settings.json, aws-cli or aws console.
Example of using aws-cli:
aws lambda update-function-configuration \
    --function-name <your-name>
    --vpc-config {"SubnetId":[...], "SecurityGroupIds": [...]}
"""

import json
import boto3
from base64 import b64decode
from training.settings import *


def decrypt_env(encrypted_env):
    decrypted_bytes = boto3.client('kms').decrypt(CiphertextBlob=encrypted_env)['Plaintext']
    return decrypted_bytes.decode('utf-8')


def get_secret(sec_name, region):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region)
    return client.get_secret_value(SecretId=sec_name)


# for Django admin static assets
INSTALLED_APPS += ['django_s3_storage']

S3_BUCKET = os.environ['DTRAIN_STATIC']
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
AWS_S3_BUCKET_NAME_STATIC = S3_BUCKET
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % S3_BUCKET
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
STATIC_ROOT = STATIC_URL


# for DB credentials
DB_ENGINE = 'django.db.backends.mysql'
USE_REMOTE_ENV = strtobool(os.environ.get('USE_REMOTE_ENV', 'false'))
USE_S3 = strtobool(os.environ.get('USE_S3', 'false'))
USE_SEC_MAN = strtobool(os.environ.get('USE_SEC_MAN', 'false'))

if USE_REMOTE_ENV:
    DB_NAME = decrypt_env(b64decode(os.environ['DJANGO_MYSQLSERVER_DB']))
    DB_USER = decrypt_env(b64decode(os.environ['DJANGO_MYSQLSERVER_USER']))
    DB_PASS = decrypt_env(b64decode(os.environ['DJANGO_MYSQLSERVER_PASS']))
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASS,
            'HOST': os.environ['DJANGO_MYSQLSERVER_HOST'],
            'PORT': os.environ['DJANGO_MYSQLSERVER_PORT'],
        },
    }

elif USE_S3:
    BUCKET_NAME = os.environ['BUCKET_NAME']
    FILE_NAME = os.environ['FILE_NAME']
    s3 = boto3.client('s3')
    encrypted_s3_content = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        ResponseContentEncoding='base64')['Body'].read(amt=1024)
    decrypted_s3_content = decrypt_env(b64decode(encrypted_s3_content))
    dj = json.loads(decrypted_s3_content)
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': dj['DJANGO_MYSQLSERVER_DB'],
            'USER': dj['DJANGO_MYSQLSERVER_USER'],
            'PASSWORD': dj['DJANGO_MYSQLSERVER_PASS'],
            'HOST': dj['DJANGO_MYSQLSERVER_HOST'],
            'PORT': dj['DJANGO_MYSQLSERVER_PORT'],
        },
    }
else:
    secret_name = os.environ['SEC_NAME']
    region_name = "us-east-1"
    response = get_secret(secret_name, region_name)
    # Ref doc, you can do either SecretString or SecretBinary
    dj = json.loads(response['SecretString'])
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': dj['username'][:-4],
            'USER': dj['username'],
            'PASSWORD': dj['password'],
            'HOST': dj['host'],
            'PORT': dj['port'],
        },
    }

