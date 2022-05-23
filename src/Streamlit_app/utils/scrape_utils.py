from utils import cleaning_utils
import pandas as pd
import json
from datetime import datetime
import glob


def load_data(file):
    with open(file, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data


def create_date_filename(data_name, data_dir, extension):
    now = datetime.now()
    date_time = now.strftime("%d%m%Y, %Hh%M")
    date_time = "_".join([_.strip() for _ in date_time.split(",")])
    filename = f"{data_name}_{date_time}"
    file_path = f'{data_dir}/{filename}.{extension}'

    return file_path


def make_numeric(gtin):
    numeric_characters = []
    for c in gtin:
        if c.isnumeric():
            numeric_characters.append(c)
    num_gtin = "".join(numeric_characters)
    # try:
    #     num_gtin = int(float(num_gtin))
    # except Exception as e:
    #     print(e)
    #     print("**************")
    #     print('num_gtin; ', num_gtin, 'gtin :', gtin)

    return num_gtin


def check_if_chain_name_already_exists(chain_name, data_dir='Data'):
    file_list = glob.glob(f'{data_dir}/*{chain_name}*.xlsx')
    if len(file_list) > 0:
        return file_list[0]
    else:
        return None
    
def is_valid_gtin(gtin):
    numeric_characters = []
    for c in gtin:
        if c.isnumeric():
            # print(c)
            numeric_characters.append(c)
    num_gtin = "".join(numeric_characters)
    if len(num_gtin) > 8:
        return True
    else: 
        return False


def preprocess_redash_data(df: pd.DataFrame):
    df.dropna(axis=0, how='any', inplace=True)
    df = df.reset_index(drop=True)
    df = df.loc[df['gtin'] != '[]']
    df['to_drop'] = df['gtin'].apply(lambda x: False if is_valid_gtin(gtin=x) else True)
    df = df.loc[df["to_drop"] == False ]
    df['gtin'] = df['gtin'].apply(lambda d: make_numeric(d))
    df = df.reset_index(drop=True)

    return df


def look_for_new_urls(new_df: pd.DataFrame, old_df: pd.DataFrame):
    old_urls = old_df['url'].to_list()
    rows = []
    urls, names, chainbrands, gtins = new_df['url'].to_list(), new_df['name'].to_list(), new_df['chainbrand'].to_list(), new_df['gtin'].to_list()
    columns = ['url', 'name', 'chainbrand', 'gtin']
    for url, name, chainbrand, gtin in zip(urls, names, chainbrands, gtins):
        if url not in old_urls:
            row = {'url': url,
                   'name': name,
                   'chainbrand': chainbrand,
                   'gtin': gtin}
            rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def collect_all_html_text(df: pd.DataFrame, meta_data: dict) -> pd.DataFrame:
    urls = df['url'].to_list()
    names = df['name'].to_list()
    chainbrands = df['chainbrand'].to_list()
    gtins = df['gtin'].to_list()
    all_collected_html, already_scrapped_urls = [], []
    columns = ['url', 'name', 'chainbrand', 'gtin', 'cleaned_html']
    for url, product, chainbrand, gtin in zip(urls, names, chainbrands, gtins):
        if url in already_scrapped_urls:
            continue
        else:
            collected_html = cleaning_utils.collect_relevant_html(url=url, tag=meta_data['tag'],
                                                                  attribute=meta_data['attribute'],
                                                                  attribute_value=meta_data['attribute_value'])
            if collected_html:
                row = {'url': url,
                       'name': product,
                       'chainbrand': chainbrand,
                       'gtin': gtin,
                       'cleaned_html': collected_html}
                all_collected_html.append(row)
                already_scrapped_urls.append(url)

    return pd.DataFrame(all_collected_html, columns=columns)


if __name__ == '__main__':
    # wanimo_df = pd.read_excel('wanimo_extracted_data.xlsx', nrows=10)
    #
    # wanimo_dict = {"tag": "div",
    #                "attribute": "class",
    #                "attribute_value": "fiche-produit-classic"}
    # df_ = collect_all_html_text(df=wanimo_df, meta_data=wanimo_dict)
    # print(df_.head(5))
    print(check_if_chain_name_already_exists(chain_name='SantéDiscount'))
