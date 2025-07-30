import pandas as pd
import os

HOME = os.environ['HOME']

conf = 't5n9'

folder_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/times/{}/'.format(HOME, conf)
excel_file = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/times/{}/{}-times.xlsx'.format(HOME, conf, conf)
excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

for folder in os.listdir(folder_path):
    if os.path.isdir(os.path.join(folder_path, folder)):
        for file in os.listdir(os.path.join(folder_path, folder)):
            if file.endswith(".csv"):
                #print(file)
                df = pd.read_csv(os.path.join(folder_path, folder, file))
                sheet_name = conf + '-' + folder + '-'+ file.split('.')[0].split('/')[-1].replace('retrieve', 'r').replace('split', 's')
                df.to_excel(excel_writer, sheet_name=sheet_name, index=False)
excel_writer.close()
