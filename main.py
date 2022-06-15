#!/usr/bin/env python


import requests
from http import HTTPStatus
import pandas as pd
import numpy as np
import os, sys
from tqdm import tqdm
import utils
import warnings
from list_names import simplified_names
from parsel import Selector
from loguru import logger as log
import post_tweet

warnings.filterwarnings('ignore')

'''
    This script is responsible for accessing the website, downloading the content, handling the tables and
    saving it in csv files.
'''


def check_last_update(url):
    response = requests.get(url, headers=utils.get_headers(), verify=False)
    if response.status_code == HTTPStatus.OK:
        website_last_update = get_last_update(response.text)
        last_recorded_update = None
        try:
            with open('datasets/last_download.txt', 'r') as f:
                last_recorded_update = f.readline()
        except FileNotFoundError as err:
            log.error(err)
        finally:
            if last_recorded_update is not None:
                last_recorded_update = last_recorded_update.split('-')[1].strip()
            log.info(f'Last recorded update: {last_recorded_update}')
            if last_recorded_update == website_last_update:
                log.info('There are no new updates')
                sys.exit(os.EX_OK)
            else:
                log.info('A new update has been found')
                processing_request(response)
                # post tweet
                post_tweet.post()
                log.info('Done.')


def get_last_update(response):
    log.info('Checking the latest document update on the website')
    selector = Selector(response)
    updated = selector.xpath('(//h4[@class="date"]/text())[1]').get().strip()
    log.info(f'Last update: {updated}')
    return str(updated)


def processing_request(response):
    log.info('Processing the data found on the website.')
    parse_tables(response)
    save_current_update_info(response)


def parse_tables(response):
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
    # table_MN = pd.read_html('datasets/content_page.dat', match='B - Indústria Extrativa')
    # print(f'Total tables: {len(table_MN)}')

    # This function reads the content.dat file, which is a html,
    # fetches the tables according to the segment and cleans up unnecessary column names.
    for seg in segments:
        for i in range(0, 2, 1):  # 0, 4, 2
            log.info(f'seg:{seg} range:{i}')
            # name formatting
            file_name = utils.slug(f'{type_file[i]}-mensal-{seg.split("-")[1]}')
            # Parse tables
            table = pd.read_html(response.content, match=seg, decimal=',', thousands='.')[i]
            # Simplified and clean
            utils.simplified_names(table, simplified_names)
            table.iloc[1:, 0] = table.iloc[1:, 0].apply(utils.clean_text)
            log.info(f'Formatting the data and creating the file: {file_name}.csv')
            # Column treatment
            for x, columns_old in enumerate(table.columns.levels):
                columns_new = np.where(columns_old.str.contains('Unnamed'), '', columns_old)
                table.rename(columns=dict(zip(columns_old, columns_new)), level=x, inplace=True)
            # Saving the file
            table.to_csv(f'datasets/{file_name}.csv', encoding='utf-8-sig')
            log.info('Saved successfully.')


def save_current_update_info(response):
    log.info('Saving current release date')
    selector = Selector(response.text)
    updated = selector.xpath('(//h4[@class="date"]/text())[1]').get().strip()
    reference_date = selector.xpath('(//p[@align="center"]/text())[1]').get().strip()

    try:
        with open('datasets/last_download.txt', 'w') as f:
            f.write(f'{reference_date} - {updated}')
        log.info('Done.')
    except:
        log.error('An error occurred while trying to save the current release date to the file.')


def main():
    log.info('Starting...')
    # Request for the page that stores the data we want.
    url = 'https://balanca.economia.gov.br/balanca/pg_principal_bc/principais_resultados.html'
    check_last_update(url)


if __name__ == '__main__':
    main()
