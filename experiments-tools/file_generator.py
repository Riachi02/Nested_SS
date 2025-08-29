import os
import random
import string
import argparse

data_parser = argparse.ArgumentParser()
data_parser.add_argument("-n", "--name", help="File name", required=True)
data_parser.add_argument("-s", "--size", help="File size in MB", required=True)

args = data_parser.parse_args()

def generate_text_file(filename: str, size_mb: float):
#    size_mb = size_mb - 0.5
    size_bytes = int(size_mb * 1024 * 1024)  # convert MB to bytes

    # caratteri stampabili, esclusi \n e \r per precisione nella dimensione
    chars = string.ascii_letters + string.digits + ' '
    print(chars)
    with open(filename, 'w', encoding='utf-8') as f:
        chunk_size = 1024 * 1024  # 1 MB per chunk
        total_written = 0
        while total_written < size_bytes:
            to_write = min(chunk_size, size_bytes - total_written)
            text = ''.join(random.choices(chars, k=to_write))
            f.write(text)
            total_written += to_write

    actual_size = os.path.getsize(filename)
    print(f"File '{filename}' creato con dimensione {actual_size / (1024 * 1024):.2f} MB")

# generate_text_file("/txts/text_10.txt", 10)
# generate_text_file("/txts/text_30.txt", 29.1)
# generate_text_file("/txts/text_50.txt", 48.2)
# generate_text_file("/txts/text_70.txt", 67.3)
# generate_text_file("/txts/text_90.txt", 86.3)
# generate_text_file("/txts/text_110.txt", 105.4)
generate_text_file(args.name, float(args.size))

