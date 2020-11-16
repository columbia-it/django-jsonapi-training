# Using AWS API Gateway

**DRAFT**

## AWS API Gateway unable to import valid OAS 3.0 spec

After some experiments trying to import our complete OAS 3.0 spec, I've found
that there are a number of limitations to AWS API Gateway:

### Can't handle parameters with square brackets:
```
Unable to put method 'GET' on resource at path '/course_terms': Invalid mapping expression specified: Validation Result: warnings : [], errors : [Parameter name should match the following regular expression: ^[a-zA-Z0-9._$-]+$]
```

Changing `page[size]` to `page_size` works -- but is incorrect. Totally breaks all the JSONAPI stuff like `filter[]`, etc.

### Can't handle http basicAuth type

```
Unsupported security definition type 'http' for 'basicAuth'. Ignoring.
```

See https://forums.aws.amazon.com/thread.jspa?threadID=305421

### Can't handle oauth2

```
Unsupported security definition type 'oauth2' for 'oauth'. Ignoring.
```

So, instead, let's just create a simple proxy for now to at least test out some of the other
AWS API GW features:

## Create a proxy+ gateway

In lieu of importing an OAS 3.0 spec, one can create a "wildcard"
[proxy+](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-http.html)
API gateway which just passes everything through to the backend, but can still add valuable gateway
functionality such as rate-limiting, OAuth 2.0 access token introspection, etc.

### A basic OAuth 2.0 API Authorization Lambda Function

See `aws/lambda_function.py` which is based on
[this example lambda function](https://github.com/awslabs/aws-apigateway-lambda-authorizer-blueprints/tree/master/blueprints/python).

I've added an `introspect()` function which simply checks for a valid active Bearer Token
and allows the API through if it is present. If the function is configured with the `scopeAlternatives`
environment variable, it also performs required scope checking. If not, the token is only checked
to make sure it is active.

First let's create some assumeable roles:

- `lambda_basic_execution` allows executing the lambda function and letting it append to the logs???
- `lambda_invoke_function_assume_apigw_role` allows the API GW authorizer to run our lambda function.

```text
$ aws iam create-role --role-name lambda_basic_execution --assume-role-policy-document file://lambda_basic_assume_role_policy.json --profile alan:CTO
{
    "Role": {
        "Path": "/",
        "RoleName": "lambda_basic_execution",
        "RoleId": "AROAZDZCSVJODEMVKCAES",
        "Arn": "arn:aws:iam::123456789012:role/lambda_basic_execution",
        "CreateDate": "2019-07-24T16:30:01Z",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    }
}
$ aws iam attach-role-policy --role-name lambda_basic_execution --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --profile alan:CTO
```

```text
$ aws iam create-policy --policy-name lambda_execute --policy-document file://lambda_execute_policy.json --profile alan:CTO

    "Policy": {
        "PolicyName": "lambda_execute",
        "PolicyId": "ANPAZDZCSVJOI4UPMG6TQ",
        "Arn": "arn:aws:iam::123456789012:policy/lambda_execute",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 0,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2019-07-24T17:42:14Z",
        "UpdateDate": "2019-07-24T17:42:14Z"
    }
}
$ aws iam create-role --role-name lambda_invoke_function_assume_apigw_role --assume-role-policy-document file://apigateway_assume_role_lambda.json --profile alan:CTO
{
    "Role": {
        "Path": "/",
        "RoleName": "lambda_invoke_function_assume_apigw_role",
        "RoleId": "AROAZDZCSVJOAQRAVLCWQ",
        "Arn": "arn:aws:iam::123456789012:role/lambda_invoke_function_assume_apigw_role",
        "CreateDate": "2019-07-24T17:30:52Z",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "lambda.amazonaws.com",
                            "apigateway.amazonaws.com"
                        ]
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    }
}
$ aws iam attach-role-policy --role-name lambda_invoke_function_assume_apigw_role --policy-arn arn:aws:iam::123456789012:policy/lambda_execute --profile alan:CTO
```

The lambda function uses environment variables to configure it so let's install both a `test` and `prod` flavor:
```text
$ rm -f lambda.zip
$ zip lambda.zip lambda_function.py
$ aws lambda create-function --function-name introspect_test --runtime python3.7 --role arn:aws:iam::123456789012:role/lambda_basic_execution  --handler lambda_function.lambda_handler --zip-file fileb://lambda.zip --environment "Variables={clientId=demo_resource_server,clientSecret=wL0pgS5RcNOgdOSSmejzZNA605d3MtkoXMVSDaJxmaTU70XnYQPOabBAYtfkWXay,introspectionUrl=https://oauth-test.cc.columbia.edu/as/introspect.oauth2}" --profile alan:CTO
$ aws lambda create-function --function-name introspect_prod --runtime python3.7 --role arn:aws:iam::123456789012:role/lambda_basic_execution  --handler lambda_function.lambda_handler --zip-file fileb://lambda.zip --environment "Variables={clientId=demo_resource_server,clientSecret=wL0pgS5RcNOgdOSSmejzZNA605d3MtkoXMVSDaJxmaTU70XnYQPOabBAYtfkWXay,introspectionUrl=https://oauth.cc.columbia.edu/as/introspect.oauth2}" --profile alan:CTO
```

TODO: Document adding `scopeAlternatives`.  For now, use the AWS Console and cut-n-paste the contents of
`scopeAlternatives.json`.

#### Testing the lambda function

You can test the lambda function in the AWS console or via the CLI as follows:

```text
$ aws lambda invoke --function-name introspect_test --payload '{  "methodArn": "arn:aws:execute-api:us-east-1:123456789012:bc28rnvr33/test/GET/v1/courses",  "authorizationToken": "Bearer y18albT1cyVRPbrt2UkSzfyM8nij"}' t.json --profile alan:CTO
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
$ cat t.json 
{"principalId": "ac45@columbia.edu", "policyDocument": {"Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Effect": "Allow", "Resource": ["arn:aws:execute-api:us-east-1:123456789012:bc28rnvr33/test/GET/v1/courses"]}]}}
```

In the above, you'll need to replace the Bearer token with an active one and make sure the required scopes
as defined in `scopeAlternatives` are set to get a succesful response.

### Import an OAS 3.0 document to speed up creating the API

There are a lot of steps in setting up an API manually. Let's use the result of a bunch of manual
setup via the AWS Console which was then exported for later re-import.

Here's the export command we used:

```text
$ aws apigateway get-export --rest-api-id bc28rnvr33 --stage-name test --export-type oas30 --parameters {"extensions":"integrations,authorizers,apigateway"} --profile alan:CTO foo.json

```

And here's the OAS 3.0 spec, with a bunch of AWS-specific extension fields:
```json
{
  "openapi" : "3.0.1",
  "info" : {
    "title" : "jsonapi proxy+",
    "version" : "2019-07-24T18:09:15Z"
  },
  "servers" : [ {
    "url" : "https://bc28rnvr33.execute-api.us-east-1.amazonaws.com/{basePath}",
    "variables" : {
      "basePath" : {
        "default" : "/test"
      }
    }
  } ],
  "paths" : {
    "/{proxy+}" : {
      "options" : {
        "responses" : {
          "200" : {
            "description" : "200 response",
            "headers" : {
              "Access-Control-Allow-Origin" : {
                "schema" : {
                  "type" : "string"
                }
              },
              "Access-Control-Allow-Methods" : {
                "schema" : {
                  "type" : "string"
                }
              },
              "Access-Control-Allow-Headers" : {
                "schema" : {
                  "type" : "string"
                }
              }
            },
            "content" : { }
          }
        },
        "x-amazon-apigateway-integration" : {
          "responses" : {
            "default" : {
              "statusCode" : "200",
              "responseParameters" : {
                "method.response.header.Access-Control-Allow-Methods" : "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'",
                "method.response.header.Access-Control-Allow-Headers" : "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                "method.response.header.Access-Control-Allow-Origin" : "'*'"
              }
            }
          },
          "requestTemplates" : {
            "application/json" : "{\"statusCode\": 200}"
          },
          "passthroughBehavior" : "when_no_match",
          "type" : "mock"
        }
      },
      "x-amazon-apigateway-any-method" : {
        "parameters" : [ {
          "name" : "proxy",
          "in" : "path",
          "required" : true,
          "schema" : {
            "type" : "string"
          }
        } ],
        "responses" : {
          "200" : {
            "description" : "200 response",
            "content" : { }
          }
        },
        "security" : [ {
          "introspection" : [ ]
        }, {
          "api_key" : [ ]
        } ],
        "x-amazon-apigateway-integration" : {
          "uri" : "http://ac45devapp01.cc.columbia.edu:9123/{proxy}/",
          "responses" : {
            "default" : {
              "statusCode" : "200"
            }
          },
          "requestParameters" : {
            "integration.request.path.proxy" : "method.request.path.proxy"
          },
          "passthroughBehavior" : "when_no_match",
          "httpMethod" : "ANY",
          "cacheNamespace" : "psuvk6",
          "cacheKeyParameters" : [ "method.request.path.proxy" ],
          "type" : "http_proxy"
        }
      }
    }
  },
  "components" : {
    "securitySchemes" : {
      "introspection" : {
        "type" : "apiKey",
        "name" : "Authorization",
        "in" : "header",
        "x-amazon-apigateway-authtype" : "custom",
        "x-amazon-apigateway-authorizer" : {
          "authorizerUri" : "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:introspect_test/invocations",
          "authorizerCredentials" : "arn:aws:iam::123456789012:role/lambda_invoke_function_assume_apigw_role",
          "authorizerResultTtlInSeconds" : 300,
          "identityValidationExpression" : "Bearer .*$",
          "type" : "token"
        }
      },
      "api_key" : {
        "type" : "apiKey",
        "name" : "x-api-key",
        "in" : "header"
      }
    }
  }
}
```

Let's import it:

```text
$ aws apigateway import-rest-api --body file://proxy+oas3.json --parameters endpointConfigurationTypes=REGIONAL --profile alan:CTO
{
    "id": "p32r23u5jb",
    "name": "jsonapi proxy+",
    "createdDate": 1563992583,
    "version": "2019-07-24T18:09:15Z",
    "apiKeySource": "HEADER",
    "endpointConfiguration": {
        "types": [
            "REGIONAL"
        ]
    }
}
```

### Deploy the API

```text
$ aws apigateway create-deployment --rest-api-id bc28rnvr33 --stage-name test --profile alan:CTO
{
    "id": "zrkle6",
    "createdDate": 1563997322
}
```

The base URL for the deployment follows the pattern
`https://<restApiId>.execute-api.<awsRegion>.amazonaws.com/<stageName>` so our's
is `https://bc28rnvr33.execute-api.us-east-1.amazonaws.com/test`.

### Next Steps

- learn more about available features such as load-balancing, rate-limiting, caching, etc.

## AWS API Developer Portal

AWS has published a serverless
[developer portal](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-developer-portal.html)
which is easily launched via a CloudFormation template.

### The portal sucks

It's not a very good developer portal and has a number of gotchas:

* Doesn't properly present the same
  [with multiple Usage Plans](https://github.com/awslabs/aws-api-gateway-developer-portal/issues/253)
  in the UI.
* The Swagger API "Try it out" functionality
  [doesn't work for "proxy+"](https://github.com/awslabs/aws-api-gateway-developer-portal/issues/297):
  The path substitution doesn't happen.
* The UI silently fails to report errors such as trying to
  [upload a large generic API definition](https://github.com/awslabs/aws-api-gateway-developer-portal/issues/296).
* No
  [restrictions on who can register for a given API](https://github.com/awslabs/aws-api-gateway-developer-portal/issues/165)
  and Usage Plan.

In short, it's nowhere near as nice as products like
[Gravitee APIM](https://gravitee.io/products/apim/)
-- which doesn't support configuring AWS API GW.
