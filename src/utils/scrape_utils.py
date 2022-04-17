from src.utils import cleaning_utils
import pandas as pd
import json
from datetime import datetime


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
    return num_gtin


def collect_all_html_text(df: pd.DataFrame, meta_data: dict) -> pd.DataFrame:
    urls = df['url'].to_list()
    names = df['name'].to_list()
    brands = df['chainbrand'].to_list()
    gtins = df['gtin'].to_list()
    all_collected_html, all_valid_urls = [], []
    columns = ['url', 'name', 'brand', 'gtin', 'cleaned_html']
    for url, product, brand, gtin in zip(urls, names, brands, gtins):
        if url in all_valid_urls:
            continue
        else:
            collected_html = cleaning_utils.collect_relevant_html(url=url, tag=meta_data['tag'],
                                                                  attribute=meta_data['attribute'],
                                                                  attribute_value=meta_data['attribute_value'])
            if collected_html:
                row = {'url': url,
                       'name': product,
                       'brand': brand,
                       'gtin': gtin,
                       'cleaned_html': collected_html}
                all_collected_html.append(row)
                all_valid_urls.append(url)

    return pd.DataFrame(all_collected_html, columns=columns)


if __name__ == '__main__':
    wanimo_df = pd.read_excel('wanimo_extracted_data.xlsx', nrows=10)

    wanimo_dict = {"tag": "div",
                   "attribute": "class",
                   "attribute_value": "fiche-produit-classic"}
    df_ = collect_all_html_text(df=wanimo_df, meta_data=wanimo_dict)
    print(df_.head(5))
