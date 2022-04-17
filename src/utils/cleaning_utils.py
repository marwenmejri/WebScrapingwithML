from bs4 import BeautifulSoup
import requests
import re
import string
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np
import random

ID_PATTERN = r"([0-9]{5,9})"
PRICE_PATTERN = r"[0-9]+\,[0-9]*\ €"
URL_PATTERN = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
MEANINGFUL_WORDS = ['product', 'brand', 'description', 'itemprop', 'price']

TAG_LIST = ['div', 'a', 'title', 'section', 'span', 'h', 'h1',
            'h2', 'h3', 'li', 'tr', 'br', 'p', 'u', 'ul', 'meta', 'article']


def create_wanted_tag_list(tag_list: list):
    wanted_tags = []
    for tag in tag_list:
        wanted_tags.append(f"<{tag}")
        wanted_tags.append(f"{tag}>")
        wanted_tags.append(f"</{tag}")
        wanted_tags.append(f"</{tag}>")
        wanted_tags.append(f"/{tag}")
    return wanted_tags


def parse_url(url):
    website = url.split('.')[1]
    return website


def filter_tag(bloc, wanted_tags):
    for tag in wanted_tags:
        if tag in bloc:
            return True
    return False


def contain_id(string):
    result_id = re.findall(ID_PATTERN, string)
    if len(result_id) > 0:
        return True
    else:
        return False


def contain_price(string):
    result_price = re.findall(PRICE_PATTERN, string)
    if len(result_price) > 0:
        return True
    else:
        return False


def contain_url(string):
    urls = re.findall(URL_PATTERN, string)
    if len(urls) > 0:
        return True
    else:
        return False


# test if a specific string is present
def contain_information(string, meaningful_words):
    for word in meaningful_words:
        if word in string:
            return True
    else:
        return False


def contain_text(string):
    if not string.startswith('<'):
        return True
    else:
        return False


def do_all_tests(string):
    all_test = []
    id_ = contain_id(string)
    all_test.append(id_)
    url = contain_url(string)
    all_test.append(url)
    text = contain_text(string)
    all_test.append(text)
    price = contain_price(string)
    all_test.append(price)
    infos = contain_information(string, meaningful_words=MEANINGFUL_WORDS)
    all_test.append(infos)
    return any(all_test)


def is_not_punct_tag_relevant(word, tag_list: list):
    punctuation = string.punctuation
    punctuation = [_ for _ in punctuation]
    listt = ["&", "@", "-", ".", "$", "/", ":", "'", ",", "+"]
    punctuation = [_ for _ in punctuation if _ not in listt]
    if word in punctuation:
        return False
    elif word in tag_list:
        return False
    elif len(word) > 40:
        return False
    else:
        return True


def clean_text(text, tag_list: list):
    text = re.sub('\n', ' ', text)
    text = re.sub('amp', '', text)
    text = re.sub('\t', ' ', text)
    text = re.sub('\r', ' ', text)
    text = re.sub('\xa0', ' ', text)

    words = word_tokenize(text)
    text = " ".join(
        [word for word in words if is_not_punct_tag_relevant(word, tag_list)])
    text = re.sub(r'[\']', ' ', text)
    text = re.sub(r'`|``', ' ', text)
    pattern = r'(\ / )|(\ /[a-z]\ )'
    text = re.sub(pattern, ' ', text)
    pattern = r'([a-z]+[0-9]*[\_]{1,3}[a-z]+[0-9]*[\_]{1,3}[0-9]*)'
    text = re.sub(pattern, ' ', text)
    pattern1 = r'([a-z]+[0-9]*\-[a-z]+[0-9]*[-]{1}[0-9]*)'
    text = re.sub(pattern1, ' ', text)
    text = text.replace("  ", " ")
    text = re.sub('--', ' ', text)
    pattern2 = r'[a-z]+[0-9]*[a-z]*[0-9]*\=[a-z]*[0-9]*[\-]*[a-z]*[0-9]*'
    text = re.sub(pattern2, ' ', text)
    text = text.replace("  ", ' ')
    return text


def collect_relevant_html(url, tag, attribute, attribute_value):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "lxml")
    extracted_html = soup.find_all(f'{tag}', {f"{attribute}": f"{attribute_value}"})
    if len(extracted_html) > 0:
        # print(f"Lenght Before Cleaning: {len(str(extracted_html[0]))} Characters")
        # print('****************************************')
        extracted_html = str(extracted_html[0])
        balise_list = extracted_html.split('>')
        balise_list = [item.replace("\n", "") + '>' for item in balise_list]
        wanted_tags = create_wanted_tag_list(tag_list=TAG_LIST)
        balise_list = [item for item in balise_list if filter_tag(
            bloc=item, wanted_tags=wanted_tags)]
        balise_list = [item for item in balise_list if do_all_tests(item)]
        body_string = '. '.join(balise_list).replace('  ', '')
        body_cleaned = clean_text(text=body_string, tag_list=TAG_LIST)
        for tag in wanted_tags:
            body_cleaned = body_cleaned.replace(tag, "")
        body_cleaned = body_cleaned.replace("  ", " ")
        # print(f"Lenght After Cleaning: {len(body_cleaned)} Characters")

        return body_cleaned


# if __name__ == '__main__':
#     df_wanimo = pd.read_excel(
#         "Data_Understanding/Excel_Files/wanimo_products.xlsx")
#     urls = list(np.unique(df_wanimo['url'].to_numpy()))
#     random_idx = random.randint(0, len(urls) - 1)
#     test_url = urls[random_idx]
#     cleaned_html = collect_relevant_html(url=test_url, tag='div',
#                                          attribute='class', attribute_value='fiche-produit-classic')
#     print(cleaned_html)