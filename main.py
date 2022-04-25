import requests
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import utils
import warnings
from list_names import simplified_names

warnings.filterwarnings('ignore')

'''
    This script is responsible for accessing the website, downloading the content, handling the tables and
    saving it in csv files.
'''


def main():
    url = 'https://balanca.economia.gov.br/balanca/pg_principal_bc/principais_resultados.html'
    # Defining which data segments we are interested in
    # As there are many tables on the site, we will use these segments as a filter
    segments = [
        'A - Agropecuária',
        'B - Indústria Extrativa',
        'C - Indústria de Transformação'
    ]
    # exp -> Export
    # imp -> Import
    type_file = {
        0: 'exp',
        1: 'imp'
    }
    # This function reads the content.dat file, which is an html,
    # fetches the tables according to the segment and cleans up unnecessary column names.

    def parse_tables():
        for seg in segments:
            for i in range(0, 2):
                # name formatting
                file_name = utils.slug(f'{type_file[i]}-mensal-{seg.split("-")[1]}')
                # Parse tables
                table = pd.read_html('datasets/content_page.dat', match=seg, decimal=',', thousands='.')[i]
                # Simplified and clean
                utils.simplified_names(table, simplified_names)
                table.iloc[1:, 0] = table.iloc[1:, 0].apply(utils.clean_text)
                print(f'Formatting the data and creating the file: {file_name}.csv')
                # Column treatment
                for x, columns_old in enumerate(table.columns.levels):
                    columns_new = np.where(columns_old.str.contains('Unnamed'), '', columns_old)
                    table.rename(columns=dict(zip(columns_old, columns_new)), level=x, inplace=True)
                # Saving the file
                table.to_csv(f'datasets/{file_name}.csv', encoding='utf-8-sig')
                print('Saved successfully.')
                print('---------------------------')
    # Request for the page that stores the data we want.
    response = requests.get(url, headers=utils.get_headers(), verify=False)
    # We save the page content in the content.dat file
    if response.status_code == 200:
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc="Downloading page.")
        # Creating the temporary content.dat file
        with open('datasets/content_page.dat', 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        # call the function
        parse_tables()
        # Delete content.dat file
        os.remove(f'datasets/content_page.dat')
    else:
        print(f'Requesting error: {response.status_code}')


if __name__ == '__main__':
    main()
