from query import QueryExecutor
import os

HOME = os.environ["HOME"]

config_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/query-configs/t5n9.yaml'.format(HOME)
outputh_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/mem-cpu/t5n9/'.format(HOME)

headers = {'Authorization': 'Basic YWRtaW46YWRtaW4='}

query_executor = QueryExecutor(config_path, headers=headers)
query_executor.execute(outputh_path)