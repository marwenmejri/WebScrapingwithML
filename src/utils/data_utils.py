import pandas as pd
import spacy
import json
from tqdm import tqdm
from spacy.tokens import DocBin
import glob
from datetime import datetime


# Export Train & Test Data to json
def load_data(file):
    with open(file, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def make_numeric(gtin):
    numeric_characters = []
    for c in gtin:
        if c.isnumeric():
            numeric_characters.append(c)
    num_gtin = "".join(numeric_characters)
    return num_gtin


def create_date_filename(data_name, data_dir, extension):
    now = datetime.now()
    date_time = now.strftime("%d%m%Y, %Hh%M")
    date_time = "_".join([_.strip() for _ in date_time.split(",")])
    filename = f"{data_name}_{date_time}"
    file_path = f'{data_dir}/{filename}.{extension}'

    return file_path


def search_for_excel_file(data_dir):
    list_of_files = glob.glob(f'{data_dir}/*.xlsx')
    if len(list_of_files) > 0:
        return True
    else:
        return False


def load_all_excel_files(data_dir):
    list_of_excel_files = glob.glob(f'{data_dir}/*.xlsx')
    all_df = pd.DataFrame()
    for excel_file in list_of_excel_files:
        one_excel_df = pd.read_excel(excel_file, index=False)
        all_df = all_df.append(one_excel_df)

    return all_df


def train_test_split(data):
    # Train Test Split
    train_size = int(len(data) * 0.8)
    test_size = train_size + int(len(data) * 0.1)
    train_data, valid_data, test_data = data[:train_size], data[train_size:test_size], data[test_size:]

    return train_data, valid_data, test_data


def create_spacy_pipeline_with_all_patterns(chainbrands, names, gtins):
    """
        Add All patterns to the Entity Ruler
    """
    nlp = spacy.blank('en')
    ruler = nlp.add_pipe("entity_ruler", last=True)
    for chainbrand, name, gtin in zip(chainbrands, names, gtins):
        ruler.add_patterns([{"label": "CHAINBRAND", "pattern": f"{chainbrand}"}])
        ruler.add_patterns([{"label": "NAME", "pattern": f"{name}"}])
        ruler.add_patterns([{"label": "NAME", "pattern": f"{name.lower()}"}])
        ruler.add_patterns([{"label": "NAME", "pattern": f"{' '.join([_ for _ in name.split()][:-1])}"}])
        ruler.add_patterns([{"label": "NAME", "pattern": f"{' '.join([_ for _ in name.split()][:-2])}"}])
        ruler.add_patterns([{"label": "NAME", "pattern": f"{' '.join([_ for _ in name.split()][:-3])}"}])
        ruler.add_patterns([{"label": "GTIN", "pattern": f"{gtin}"}])
    return nlp


def parse_train_data(doc, nlp):
    """
        Create a sample of training data by passing the html text (doc) to the spacy entity ruler (nlp) and return a tuple (text, a dict of
        entities) source to the spacy documentation https://spacy.io/usage/training#training-data
    """
    detections = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
    return doc.text, {'entities': detections}


def create_training(data):
    """
        convert spaCy’s previous JSON format to the new binary format ".spacy"
    """
    nlp = spacy.blank("en")
    db = DocBin()
    for text, annotations in tqdm(data):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode='contract')
            if span is None:
                print('Skipping entity')
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    return db


if __name__ == '__main__':
    all_df_ = load_all_excel_files(data_dir='Data')
    print(all_df_.head())
    print(len(all_df_))
