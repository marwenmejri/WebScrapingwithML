from src.utils import redash_utils as redash
from src.utils import scrape_utils
from dotenv import load_dotenv
import os



def collect_data(redash_url, api_key, chain_id, n_samples=300, data_dir='../../Data'):
    """
    Function: make a request to the Redash API to collect data (urls + desired outputs) from a data-source and then scrap
    all collected urls, finally preprocess all collected html data (cleaning)
    :param redash_url: credential to create a Redash session
    :param api_key: credential to create a Redash session
    :param chain_id: int: chainbrand that we want to collect data for
    :param n_samples: int: nbr of rows to collect
    :param data_dir: Directory where to save collected raw data
    :return: saved file path (Excel file containing collected data)
    """

    # query to grab the name specific to the chain_id parameter
    query1 = f"select name from chain where id={chain_id};"
    chain_name = redash.get_chain_name(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query1)
    # create Excel file name
    file_path = scrape_utils.create_date_filename(data_name=chain_name, data_dir=data_dir, extension='xlsx')
    # load the correct metadata(dict containing html section to scrap) specific to this chainbrand name
    meta_data = scrape_utils.load_data('../../meta-data.json')
    chain_metadata = meta_data[chain_name]

    # query to collect all related data specific to the chain_id params
    query2 = f"select url, data, parent_remoteid, name, created, updated, chainbrand, premoteid, gtin, id, " \
             f"chain_id  from chainproduct where  created >'01/03/2022 09:59' and chain_id={chain_id} limit {n_samples} ; "
    df = redash.get_raw_data(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query2)

    # Preprocess the raw data : drop rows with nan value, transform gtin column
    df.dropna(axis=0, how='any', inplace=True)
    df = df.reset_index(drop=True)
    df = df.loc[df['gtin'] != '[]']
    df['gtin'] = df['gtin'].apply(lambda d: scrape_utils.make_numeric(d))
    df = df.reset_index(drop=True)

    # collect needed html data for all resulting urls from query 2
    collected_data = scrape_utils.collect_all_html_text(df=df, meta_data=chain_metadata)

    # save scrapped data + desired output to an excel file
    collected_data.to_excel(file_path)

    return file_path


if __name__ == '__main__':
    load_dotenv()
    REDASH_HOST = os.getenv('REDASH_HOST')
    API_KEY = os.getenv('API_KEY')

    N_SAMPLES = 50
    CHAIN_ID = 316
    collect_data(redash_url=REDASH_HOST, api_key=API_KEY, chain_id=CHAIN_ID, n_samples=N_SAMPLES)

