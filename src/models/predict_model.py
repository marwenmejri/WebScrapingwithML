import spacy
from spacy import displacy
from src.utils import model_utils
from src.utils import cleaning_utils


def make_predictions(url, website, meta_data_path='meta-data.json', use_last_trained_model=True):
    """
    Function to make prediction with the trained model
    :param url: str: url to extract information(make detections) on it
    :param website: str: Chain name (Expl: Wanimo, SantéDiscount...)
    :param meta_data_path: dict(json_file): metadata(dict containing html section to scrap) specific to all chain name
    used to train our models
    :param use_last_trained_model: boolean: it indicates the use of the last trained ner model
    :return: None
    """
    meta_data = model_utils.load_data(meta_data_path)
    if website in list(meta_data.keys()):
        data = meta_data[website]
        cleaned_html = cleaning_utils.collect_relevant_html(url=url, tag=data['tag'], attribute=data['attribute'],
                                                            attribute_value=data['attribute_value'])
        if cleaned_html:
            if use_last_trained_model:
                last_trained_model_path = model_utils.get_last_trained_model()
                loaded_model = spacy.load(f'{last_trained_model_path}/model-last')
            else:
                while True:
                    try:
                        user_trained_model_path = input('Enter a Trained Model Path: ')
                        loaded_model = spacy.load(user_trained_model_path)
                        break
                    except Exception as e:
                        print('You Entered a wrong Model Path!! Try to Enter a Valid one')
            colors = {'NAME': "#85C1E9", "BRAND": "#ff6961", "GTIN": "#00969e"}
            options = {"ents": ['NAME', 'BRAND'], "colors": colors}
            displacy.serve(loaded_model(cleaned_html), style='ent',
                           port=8000, host="127.0.0.1", options=options)
        else:
            return 'Choose a Valid Url'
    else:
        return "Please enter a correct website url"


if __name__ == '__main__':
    # URL = 'https://www.wanimo.com/fr/furets/jouet-pour-furet-sc201/tunnel-reversible-deluxe-sf5751/'
    # URL = 'https://www.wanimo.com/fr/chats/alimentation-pour-chat-sc6/lily-s-kitchen-tasty-cuts-sf22308/'
    # WEBSITE = 'Wanimo'

    URL = 'https://www.santediscount.com/lero-spiruline-bio-60-comprimes.html'
    WEBSITE = 'SantéDiscount'
    make_predictions(url=URL, website=WEBSITE, use_last_trained_model=True)
