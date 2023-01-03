#!/usr/bin/env python
"""
This piece of program is a simple demo of using rds data service to do housework
when an Aurora Serverless DB cluster doesn't have a public IP address.

Turn on logging.DEBUG to see how it works.

To add more functions, please refer to the following links:
https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds-data.html
"""
import boto3
import os
import sys
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s: %(message)s"
                    )
log = logging.getLogger(__name__)

database_name = os.environ['DB_NAME']
db_cluster_arn = os.environ['DB_CLUSTER_ARN']
db_credentials_secrets_store_arn = os.environ['DB_SECRETS_STORE_ARN']

# data api client
rds_client = boto3.client('rds-data')


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        log.info(f'Function: {f.__name__}')
        log.info(f'*  args: {args}')
        log.info(f'*  kw: {kw}')
        log.info(f'*  execution time: {(te-ts)*1000:8.2f} ms')
        return result
    return timed


@timeit
def execute_statement(sql, sql_parameters=[]):
    response = rds_client.execute_statement(
        secretArn=db_credentials_secrets_store_arn,
        database=database_name,
        resourceArn=db_cluster_arn,
        sql=sql,
        parameters=sql_parameters
    )
    return response


def simple_query(sql):

    log.info('SQL: %s', sql)

    try:
        response = execute_statement(sql)
    except Exception as e:
        log.error(e)
        return

    records = response['records']
    if not records:
        log.info("Nod data rows")
        return

    results = format_query_results(response)
    for i in results:
        log.info(i)


# formatting results
def format_query_results(results):

    log.info('===== query results =====')

    # Formatting query returned Field
    def format_field(field):
        return list(field.values())[0]

    # Formatting query returned Record
    def format_record(record):
        return [format_field(field) for field in record]

    # Formatting query returned Field
    def format_records(records):
        return [format_record(record) for record in records]

    return format_records(results['records'])


def main():
    if len(sys.argv) != 2:
        log.info("Usage: %s <sql statement>" % sys.argv[0])
        return
    simple_query(sys.argv[1])


if __name__ == '__main__':
    main()
