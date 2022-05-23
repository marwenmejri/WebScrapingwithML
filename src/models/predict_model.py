from src.utils import model_utils
from src.utils import cleaning_utils

import spacy
from spacy import displacy


def make_predictions(url, website, use_last_trained_model=True, meta_data_path='meta-data.json'):
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
                loaded_model = spacy.load(
                    f'{last_trained_model_path}/model-last')
            else:
                while True:
                    try:
                        user_trained_model_path = input(
                            'Enter a Trained Model Path: ')
                        loaded_model = spacy.load(user_trained_model_path)
                        break
                    except Exception as e:
                        print('You Entered a wrong Model Path!! Try to Enter a Valid one')

            doc = loaded_model(str(cleaned_html))
            predictions = [{ent.label_: ent.text} for ent in doc.ents]
            new_dict = {}
            for pred in predictions:
                if list(pred.keys())[0] not in list(new_dict.keys()):
                    new_dict[list(pred.keys())[0]] = [list(pred.values())[0]]
                else:
                    new_dict[list(pred.keys())[0]].append(list(pred.values())[0])
            for key, value in new_dict.items():
                new_dict[key] = set(value)

            print(f"\n \n **** Predictions **** : {new_dict}")

            colors = {'NAME': "#85C1E9", "CHAINBRAND": "#ff6961", "GTIN": "#00969e", "PRICE": "#00969e"}
            options = {"ents": ['NAME', 'CHAINBRAND', 'GTIN', 'PRICE'], "colors": colors}
            displacy.serve(loaded_model(str(cleaned_html)), style='ent', port=8000, host="127.0.0.1", options=options)

        else:
            return 'Choose a Valid Url'
    else:
        return "Please enter a correct website url"


if __name__ == '__main__':
    # URL = 'https://www.cocooncenter.com/propolis-redon-pastilles-miel-propolis-bio-24-pastilles/80120.html'
    # WEBSITE = 'Cocooncenter'

    # URL = 'https://www.wanimo.com/fr/chats/alimentation-pour-chat-sc6/lily-s-kitchen-tasty-cuts-sf22308/'
    # WEBSITE = 'Wanimo'

    URL = 'https://www.santediscount.com/lero-spiruline-bio-60-comprimes.html'
    WEBSITE = 'SantéDiscount'
    print(make_predictions(url=URL, website=WEBSITE, use_last_trained_model=True))
