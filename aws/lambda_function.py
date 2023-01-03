# based on https://github.com/awslabs/aws-apigateway-lambda-authorizer-blueprints/tree/master/blueprints/python
import re
import os
import json
from botocore.vendored import requests

def lambda_handler(event, context):
    """
    Event looks like the following and MethodArn is split() into arn[] and path[]
        arn[]:      0   1   2           3         4            5
                                                       path[]: 0          1    2   3:
    {
      "methodArn": "arn:aws:execute-api:us-east-1:999999999999:bc28rnvr33/test/GET/v1/courses",
      "authorizationToken": "Bearer SStvHK9n9LZLHRwRehNxnW7AOSqI"
    }
    """
    print("Client token: " + event['authorizationToken'])
    print("Method ARN: " + event['methodArn'])
    arn = event['methodArn'].split(':')
    path = arn[5].split('/')
    verb = path[2]
    resource = '/'+ '/'.join(path[3:])
    awsAccountId = arn[4]
    principalId = introspect(event['authorizationToken'], verb, resource)
    if principalId:
        policy = AuthPolicy(principalId, awsAccountId)
        policy.restApiId = path[0]
        policy.region = arn[3]
        policy.stage = path[1]
        policy.allowMethod(verb, resource)
    else:
        raise Exception('Unauthorized')

    authResponse = policy.build()
    return authResponse

def introspect(authheader, verb, resource):
    """
    invoke the introspection endpoint and return 'sub' or None
    expects the following environment variables:
    - introspectionUrl: URL of OAuth2.0 AS's introspection endpoint.
    - clientId: OAuth 2.0 AS's client ID for a client allowed to introspect.
    - clientSecret: client secret for clientId
    - scopeAlternatives: optional JSON map of arrays of alternative required scopes for 
      given method and path pattern.
      for example:
        {
          "GET/v1/courses/?$": [
            ["auth-columbia", "read", "foobar"],
            ["auth-columbia", "read", "blather"]
          ],
          "GET/v1/courses/[^/]+/?$": [
            ["auth-columbia", "read", "foobar"],
            ["auth-columbia", "read", "plugh"]
          ]
        }
    """
    introspectionUrl = os.environ.get('introspectionUrl')
    clientId = os.environ.get('clientId')
    clientSecret = os.environ.get('clientSecret')
    scopeAlternativesStr = os.environ.get('scopeAlternatives')
    scopeAlternatives = json.loads(scopeAlternativesStr) if scopeAlternativesStr else None

    print("introspecting {} via {}".format(authheader, introspectionUrl))
    if not authheader.startswith('Bearer '):
        print("not a Bearer token")
        return None
    token = authheader[len('Bearer '):]
    response = requests.post(introspectionUrl, auth=(clientId, clientSecret), data={'token': token})
    print(response.status_code, response.json())
    if response.status_code != 200:
        return None
    intro_result = response.json()
    if ('active' in intro_result and intro_result['active']
        and check_scope_alternatives(verb, resource, intro_result, scopeAlternatives)):
        return intro_result['sub'] if 'sub' in intro_result else 'nouser'
    else:
        return None

def check_scope_alternatives(verb, resource, intro_result, alts):
    """
    check to see if one of the required lists of scopes and return True or False.
    if no alts were configured, then just return True.
    """
    verb_resource = verb + resource
    print("checking required scopes for {}".format(verb_resource))
    if alts is None:
        print("permission granted: no required scopes")
        return True
    for pattern in alts:
        if re.match(pattern, verb_resource):
            scopes = set(intro_result['scope'].split()) if 'scope' in intro_result else {}
            for num, allowed in enumerate(alts[pattern]):
                if set(allowed).issubset(scopes):
                    print("permission granted for {} by pattern '{}' scope rule {}".format(verb_resource, pattern, num))
                    return True
            print("permission denied for {}: no matching scope rules for pattern '{}'".format(verb_resource, pattern))
            return False
    print("permssion denied: {} is not matched in alternative scope rules".format(verb_resource))
    return False


class HttpVerb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


class AuthPolicy(object):
    # The policy version used for the evaluation. This should always be '2012-10-17'
    version = '2012-10-17'
    # The regular expression used to validate resource paths for the policy
    pathRegex = '^[/.a-zA-Z0-9-\*]+$'
    # The API Gateway API id. By default this is set to '*'
    restApiId = '*'
    # The region where the API is deployed. By default this is set to '*'
    region = '*'
    # The name of the stage used in the policy. By default this is set to '*'
    stage = '*'

    def __init__(self, principal, awsAccountId):
        self.awsAccountId = awsAccountId
        self.principalId = principal
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):
        '''Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null.'''
        if verb != '*' and not hasattr(HttpVerb, verb):
            raise NameError('Invalid HTTP verb ' + verb + '. Allowed verbs in HttpVerb class')
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError('Invalid resource path: ' + resource + '. Path should match ' + self.pathRegex)

        if resource[:1] == '/':
            resource = resource[1:]

        resourceArn = 'arn:aws:execute-api:{}:{}:{}/{}/{}/{}'.format(self.region, self.awsAccountId, self.restApiId, self.stage, verb, resource)

        if effect.lower() == 'allow':
            self.allowMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })
        elif effect.lower() == 'deny':
            self.denyMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })

    def _getEmptyStatement(self, effect):
        '''Returns an empty statement object prepopulated with the correct action and the
        desired effect.'''
        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': []
        }

        return statement

    def _getStatementForEffect(self, effect, methods):
        '''This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy.'''
        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod['conditions'] is None or len(curMethod['conditions']) == 0:
                    statement['Resource'].append(curMethod['resourceArn'])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement['Resource'].append(curMethod['resourceArn'])
                    conditionalStatement['Condition'] = curMethod['conditions']
                    statements.append(conditionalStatement)

            if statement['Resource']:
                statements.append(statement)

        return statements

    def allowAllMethods(self):
        '''Adds a '*' allow to the policy to authorize access to all methods of an API'''
        self._addMethod('Allow', HttpVerb.ALL, '*', [])

    def denyAllMethods(self):
        '''Adds a '*' allow to the policy to deny access to all methods of an API'''
        self._addMethod('Deny', HttpVerb.ALL, '*', [])

    def allowMethod(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy'''
        self._addMethod('Allow', verb, resource, [])

    def denyMethod(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy'''
        self._addMethod('Deny', verb, resource, [])

    def allowMethodWithConditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._addMethod('Allow', verb, resource, conditions)

    def denyMethodWithConditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._addMethod('Deny', verb, resource, conditions)

    def build(self):
        '''Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy.'''
        if ((self.allowMethods is None or len(self.allowMethods) == 0) and
                (self.denyMethods is None or len(self.denyMethods) == 0)):
            raise NameError('No statements defined for the policy')

        policy = {
            'principalId': self.principalId,
            'policyDocument': {
                'Version': self.version,
                'Statement': []
            }
        }

        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Allow', self.allowMethods))
        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Deny', self.denyMethods))

        return policy
