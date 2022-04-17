import pandas as pd
from src.utils import data_utils
import random


def annotate_data(data_dir='../../Data'):
    """
    function to transform raw data to a json formatted data (annotate all html text previously collected by the
    scraping job) by passing all html texts to a spaCy pipeline(Entity Ruler), split annotated data to training,
    validating and testing sets and finally convert all json partitions of data to the binary spaCy format
    :param data_dir: Directory where to save all data
    :return: None
    """

    # Grab the last created Excel file (the latest raw data)
    latest_created_raw_data_path = data_utils.search_for_last_created_excel_file(data_dir=data_dir)
    if latest_created_raw_data_path:
        df = pd.read_excel(latest_created_raw_data_path)
    else:
        print("There is no Raw Data present in the Data Directory")

    # Annotate all html texts with spaCy Entity ruler
    names, brands, gtins, all_html = df['name'], df['brand'], df['gtin'], df['cleaned_html']
    nlp = data_utils.create_spacy_pipeline_with_all_patterns(brands=brands, names=names, gtins=gtins)
    annotated_data = [data_utils.parse_train_data(doc=d, nlp=nlp) for d in nlp.pipe(all_html)]
    # Create a dated filename to name the new resultant json annotated data
    annotated_data_name = data_utils.create_date_filename(data_name='annotated_data',
                                                          data_dir=data_dir, extension='json')

    # Check if there is an old annotated json data present in the data directory
    latest_annotated_data_path = data_utils.training_data_already_exists(data_dir=data_dir, extension='json')
    # print(latest_annotated_data_path)

    # if the data directory is empty, we will proceed by splitting and saving all json partions of data
    if latest_annotated_data_path is None:
        # print("latest_annotated_data_path is None")
        data_utils.save_data(file=annotated_data_name, data=annotated_data)
        train_data, valid_data, test_data = data_utils.train_test_split(data=annotated_data)
        train_data_name = data_utils.create_date_filename(data_name='train_data', data_dir=data_dir,
                                                          extension='json')
        data_utils.save_data(file=train_data_name, data=train_data)
        valid_data_name = data_utils.create_date_filename(data_name='valid_data', data_dir=data_dir,
                                                          extension='json')
        data_utils.save_data(file=valid_data_name, data=valid_data)
        test_data_name = data_utils.create_date_filename(data_name='test_data', data_dir=data_dir,
                                                         extension='json')
        data_utils.save_data(file=test_data_name, data=test_data)
    # If old data exist in the data directory, we will first join all new and old json annotated data together and then
    # split and save all resultant sets of data
    else:
        # print("latest_annotated_data_path Exist")
        # load the old existent data
        latest_annotated_data = data_utils.load_data(file=latest_annotated_data_path)
        # print(len(latest_annotated_data))
        all_annotated_data = latest_annotated_data + annotated_data
        # We need to shuffle the new concatenated data
        random.shuffle(all_annotated_data)
        data_utils.save_data(file=annotated_data_name, data=all_annotated_data)
        train_data, valid_data, test_data = data_utils.train_test_split(data=all_annotated_data)
        train_data_name = data_utils.create_date_filename(data_name='train_data', data_dir=data_dir,
                                                          extension='json')
        data_utils.save_data(file=train_data_name, data=train_data)
        valid_data_name = data_utils.create_date_filename(data_name='valid_data', data_dir=data_dir,
                                                          extension='json')
        data_utils.save_data(file=valid_data_name, data=valid_data)
        test_data_name = data_utils.create_date_filename(data_name='test_data', data_dir=data_dir,
                                                         extension='json')
        data_utils.save_data(file=test_data_name, data=test_data)

    # Convert Annotated data to the spaCy Format and save the results
    train_spacy = data_utils.create_training(data=train_data)
    train_spacy_filename = data_utils.create_date_filename(data_name='train_data',
                                                           data_dir=data_dir, extension='spacy')
    train_spacy.to_disk(train_spacy_filename)
    valid_spacy = data_utils.create_training(data=valid_data)
    valid_spacy_filename = data_utils.create_date_filename(data_name='test_data',
                                                           data_dir=data_dir, extension='spacy')
    valid_spacy.to_disk(valid_spacy_filename)
    test_spacy = data_utils.create_training(data=test_data)
    test_spacy_filename = data_utils.create_date_filename(data_name='valid_data',
                                                          data_dir=data_dir, extension='spacy')
    test_spacy.to_disk(test_spacy_filename)


if __name__ == '__main__':
    annotate_data()


