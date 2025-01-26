#!/usr/bin/env python3

import subprocess
import os
import argparse
import zipfile
import shutil

def parse_args():
    parser = argparse.ArgumentParser(description='Download data from the internet.')
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=True,
        help='Input text file containing the accession numbers.'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=True,
        help='Output path.'
    )

    args = parser.parse_args()
    return args

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

if __name__ == '__main__':
    args = parse_args()

    input_file = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    data_path = os.path.join(output_path, 'data')

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        os.makedirs(data_path)

    # Read the input file
    assembly_accessions = []
    with open(input_file, 'r') as file:
        lines = file.readlines()[1:] # Skip the first line ("Assembly Accession")
        for line in lines:
            accession_number = line.strip()
            if accession_number:  # Skip empty lines
                assembly_accessions.append(accession_number)
    
    print(f'Found {len(assembly_accessions)} assembly accessions.')

    # Download the data
    i = 1
    e = 0
    for accession in assembly_accessions:
        print(f'Downloading {accession} ({i}/{len(assembly_accessions)})...')
        cmd = f"datasets download genome accession {accession} --include genome"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f'{accession} downloaded successfully.')

            print(f'Unzipping and moving the files...')

            unzip_file('ncbi_dataset.zip', data_path) # unzip the downloaded file

            # Move the genome 
            ncbi_data_path = os.path.join(data_path, 'ncbi_dataset', 'data', accession)
            for root, dirs, files in os.walk(ncbi_data_path):
                    for file in files:
                        if file.endswith('.fna'):
                            shutil.move(os.path.join(root, file), os.path.join(data_path, file))

            # Remove the unnecessary files
            os.remove('ncbi_dataset.zip')
            shutil.rmtree(os.path.join(data_path, 'ncbi_dataset'))
            os.remove(os.path.join(data_path, 'md5sum.txt'))
            os.remove(os.path.join(data_path, 'README.md'))
        
        else:
            print(f'ERROR: {result.stderr}')
            subprocess.run(f"rm ncbi_dataset.zip", shell=True)
            e += 1

        i += 1

    shutil.move(input_file, output_path)

    print('Download process finished. Input file moved to the output directory.')
    if e > 0:
        print(f'{e} errors occurred during the download process. {i - e} files were downloaded.')
    else:
        print('All files were downloaded successfully.')