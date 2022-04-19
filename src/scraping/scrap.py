import pandas as pd

from src.utils import redash_utils as redash
from src.utils import scrape_utils
from dotenv import load_dotenv
import os


def collect_data(redash_url, api_key, chain_id_list: list, n_samples=300, data_dir='../../Data'):
    """
    Function: make a request to the Redash API to collect data (urls + desired outputs) from a data-source and then scrap
    all collected urls, finally preprocess all collected html data (cleaning)
    :param redash_url: credential to create a Redash session
    :param api_key: credential to create a Redash session
    :param chain_id_list: list[int]: list of chainbrand ids that we want to collect data for
    :param n_samples: int: nbr of rows to collect
    :param data_dir: Directory where to save collected raw data
    :return: saved file path (Excel file containing collected data)
    """

    all_files_paths = []
    for chain_id in chain_id_list:
        # query to grab the name specific to the chain_id parameter
        query1 = f"select name from chain where id={chain_id};"
        chain_name = redash.get_chain_name(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query1)

        # create Excel file name
        file_path = scrape_utils.create_date_filename(data_name=chain_name, data_dir=data_dir, extension='xlsx')
        all_files_paths.append(file_path)

        # load the correct metadata(dict containing html section to scrap) specific to this chainbrand name
        meta_data = scrape_utils.load_data('../../meta-data.json')
        chain_metadata = meta_data[chain_name]

        # query to collect all related data specific to the chain_id params
        query2 = f"select url, name, created, updated, chainbrand, premoteid, gtin, id, chain_id  from chainproduct " \
                 f"where created >'01/03/2022 09:59' and chain_id={chain_id} limit {n_samples} ; "
        df = redash.get_raw_data(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query2)

        # Preprocess the raw data : drop rows with nan value, transform gtin column
        df = scrape_utils.preprocess_redash_data(df=df)

        # Check if this Chainbrand has been already used to construct our data
        chain_name_excel_file = scrape_utils.check_if_chain_name_already_exists(chain_name=chain_name, data_dir=data_dir)

        if chain_name_excel_file:
            old_df = pd.read_excel(chain_name_excel_file, index=False)
            non_seen_urls_df = scrape_utils.look_for_new_urls(new_df=df, old_df=old_df)
            # collect html data for all new urls specific to this chainbrand
            collected_data = scrape_utils.collect_all_html_text(df=non_seen_urls_df, meta_data=chain_metadata)
        else:
            # collect needed html data for all resulting urls from query 2
            collected_data = scrape_utils.collect_all_html_text(df=df, meta_data=chain_metadata)

        # save scrapped data + desired output to an excel file
        collected_data.to_excel(file_path, index=False)

    return all_files_paths


if __name__ == '__main__':
    load_dotenv()
    REDASH_HOST = os.getenv('REDASH_HOST')
    API_KEY = os.getenv('API_KEY')

    N_SAMPLES = 30
    CHAIN_IDS = [33, 200, 201]
    collect_data(redash_url=REDASH_HOST, api_key=API_KEY, chain_id_list=CHAIN_IDS, n_samples=N_SAMPLES)

