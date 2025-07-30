import pandas as pd
import os
from config_tools import ConfigGenerator
from datetime import datetime

HOME = os.environ['HOME']
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

folder_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/times/t5n9/'.format(HOME)
outputh_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/query-configs/t5n9/'.format(HOME)

config_generator = ConfigGenerator(proto='http',url='172.17.7.37',port=9090, site="docker")

for folder in os.listdir(folder_path):
    if os.path.isdir(os.path.join(folder_path, folder)):
        for file in os.listdir(os.path.join(folder_path, folder)):
            if file.endswith(".csv"):
                #print(os.path.join(folder, file))
                df = pd.read_csv(os.path.join(folder_path, folder, file))
                #elapsed_mean = df['elapsed'].mean()
                #if elapsed_mean <= 1:
                start_time = df['start'].iloc[0]
                end_time = df['end'].iloc[-1]
                metric_params = {
                    "name": 't5-n9-memory-' + folder + '-' + file.split('.')[0],
                    "query": 'container_memory_working_set_bytes{image="docker-ss-node"}',
                    "start_time": start_time,
                    "end_time": end_time,
                    "step": "1s"
                }
                config_generator.add_metric(metric_params)
                time_interval = str(int(datetime.strptime(end_time, DATE_FORMAT).timestamp() - datetime.strptime(start_time, DATE_FORMAT).timestamp()))
                metric_params = {
                    "name": 't5-n9-cpu-' + folder + '-' + file.split('.')[0],
                    "query": 'rate(container_cpu_usage_seconds_total{image="docker-ss-node"}['+ time_interval + 's])',
                    "start_time": datetime.fromtimestamp(int(datetime.strptime(end_time, DATE_FORMAT).timestamp()) -1).strftime(DATE_FORMAT),
#                    "start_time": start_time,
                    "end_time": end_time,
                    "step": "1s"
                }
                config_generator.add_metric(metric_params)
config_generator.save_config()
