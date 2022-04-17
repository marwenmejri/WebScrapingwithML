import json
import requests
from dotenv import load_dotenv
import os
import pandas as pd


# Create Query
def create_query(redash_url, api_key, chain_id, query):
    params = {
            "data_source_id": 6,
            "query": f"{query}",
            "name": f"{chain_id}_Query"
             }
    path = "{}/api/queries".format(redash_url)
    headers = {'Authorization': 'Key {}'.format(api_key)}
    response = requests.post(path, headers=headers, data=json.dumps(params))
    if response.status_code != 200:
        raise Exception('Refresh failed.')
    json_response = json.loads(response.text)

    return json_response


# Generate Query Result
def generate_query_results(redash_url, api_key, query_id):
    path = "{}/api/queries/{}/results".format(redash_url, query_id)
    headers = {'Authorization': 'Key {}'.format(api_key), 'Content-Type': 'application/json'}
    response = requests.post(path, headers=headers)
    json_response = json.loads(response.text)

    return json_response


def get_raw_data(redash_url, api_key, chain_id, query):
    i = 0
    while i < 3:
        try:
            i += 1
            json_response1 = create_query(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query)
            query_id = json_response1['id']
            json_response2 = generate_query_results(redash_url=redash_url, api_key=api_key, query_id=query_id)
            rows = json_response2['query_result']['data']['rows']
            break
        except KeyError as k:
            print("KeyError Exception occurred : ", k)
            print(f"*** Request Attempt n° {i} Has Failed ***")

    return pd.DataFrame(rows)


def get_chain_name(redash_url, api_key, chain_id, query):
    i = 0
    while i < 3:
        try:
            i += 1
            json_response1 = create_query(redash_url=redash_url, api_key=api_key, chain_id=chain_id, query=query)
            query_id = json_response1['id']
            json_response2 = generate_query_results(redash_url=redash_url, api_key=api_key, query_id=query_id)
            chain_name = json_response2['query_result']['data']['rows'][0]['name']
            break
        except KeyError as k:
            print("KeyError Exception occurred : ", k)
            print(f"*** Request Attempt n° {i} Has Failed ***")

    return chain_name


# if __name__ == '__main__':
#     load_dotenv()
#     REDASH_HOST = os.getenv('REDASH_HOST')
#     API_KEY = os.getenv('API_KEY')
#     N_SAMPLES = 1000
#     CHAIN_ID = 316
#     query1 = f"select url, data, parent_remoteid, name, created, updated, chainbrand, " \
#              f"premoteid, gtin, id, chain_id,  from chainproduct where  created >'01/01/2021 09:59' and " \
#              f"chain_id={CHAIN_ID} limit {N_SAMPLES} ; "
#     df_ = get_raw_data(redash_url=REDASH_HOST, api_key=API_KEY, chain_id=CHAIN_ID, query=query1)
#     print(df_.head(5))
#
#     query2 = f"select name from chain where id={CHAIN_ID};"
#     chain_name_ = get_chain_name(redash_url=REDASH_HOST, api_key=API_KEY, chain_id=CHAIN_ID, query=query2)
#     print(chain_name_)
