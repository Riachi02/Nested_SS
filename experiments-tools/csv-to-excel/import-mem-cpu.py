import pandas as pd
import os

HOME = os.environ['HOME']

folder_path = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/mem-cpu/t5n9/'.format(HOME)
excel_file = '{}/samothrace-pseudonymization/experiments-tools/csv-to-excel/mem-cpu/t5n9/t5n9-resources.xlsx'.format(HOME)

excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(folder_path, file))
        sheet_name = "t5n9-" + file.split('.')[0].split('-',2)[2]
        df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

""" for dim_folder in os.listdir(folder_path):
    if os.path.isdir(os.path.join(folder_path, dim_folder)):
        for op_folder in os.listdir(os.path.join(folder_path, dim_folder)):
            if os.path.isdir(os.path.join(folder_path, dim_folder, op_folder)):
                for file in os.listdir(os.path.join(folder_path, dim_folder, op_folder)):
                    if file.endswith(".csv"):
                        df = pd.read_csv(os.path.join(folder_path, dim_folder, op_folder, file))
                        sheet_name = "t4n7-" + dim_folder + '-'+ op_folder + '-' + file.split('.')[0].split('_')[1]
                        df.to_excel(excel_writer, sheet_name=sheet_name, index=False) """
excel_writer.close()

