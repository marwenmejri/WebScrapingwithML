from src.utils import data_utils
import random


def annotate_data(data_dir='../../Data', save_data=True):
    """
    function to transform raw data to a json formatted data (annotate all html text previously collected by the
    scraping job) by passing all html texts to a spaCy pipeline(Entity Ruler), split annotated data to training,
    validating and testing sets and finally convert all json partitions of data to the binary spaCy format
    :param save_data: bool: default True: we will save the spaCy binary formatted data
    :param data_dir: Directory where to save all data
    :return: None
    """

    # Load all Excel file and merge them in one big Pandas DataFrame
    raw_data_exist = data_utils.search_for_excel_file(data_dir=data_dir)
    if not raw_data_exist:
        print("There is no Raw Data present in the Data Directory")
    else:
        all_data_df = data_utils.load_all_excel_files(data_dir=data_dir)
        # Annotate all html texts with spaCy Entity ruler
        names, chainbrands, gtins, all_html = all_data_df['name'], all_data_df['chainbrand'], all_data_df['gtin'], all_data_df['cleaned_html']
        nlp = data_utils.create_spacy_pipeline_with_all_patterns(chainbrands=chainbrands, names=names, gtins=gtins)
        annotated_data = [data_utils.parse_train_data(doc=d, nlp=nlp) for d in nlp.pipe(all_html)]
        # We need to shuffle the new annotated data
        random.shuffle(annotated_data)

        # Create a dated filename to name the resultant json annotated data (and save it to the data directory)
        # annotated_data_name = data_utils.create_date_filename(data_name='annotated_data',
        #                                                       data_dir=data_dir, extension='json')
        # data_utils.save_data(file=annotated_data_name, data=annotated_data)

        # we will proceed by splitting and saving just json tes partition of data
        train_data, valid_data, test_data = data_utils.train_test_split(data=annotated_data)
        if save_data:
            test_data_name = data_utils.create_date_filename(data_name='test_data', data_dir=data_dir,
                                                             extension='json')
            data_utils.save_data(file=test_data_name, data=test_data)

        # Convert Annotated data to the spaCy Format and save the results if the saving params is True
        train_spacy = data_utils.create_training(data=train_data)
        valid_spacy = data_utils.create_training(data=valid_data)
        test_spacy = data_utils.create_training(data=test_data)

        if save_data:
            train_spacy_filename = data_utils.create_date_filename(data_name='train_data',
                                                                   data_dir=data_dir, extension='spacy')
            train_spacy.to_disk(train_spacy_filename)
            valid_spacy_filename = data_utils.create_date_filename(data_name='test_data',
                                                                   data_dir=data_dir, extension='spacy')
            valid_spacy.to_disk(valid_spacy_filename)
            test_spacy_filename = data_utils.create_date_filename(data_name='valid_data',
                                                                  data_dir=data_dir, extension='spacy')
            test_spacy.to_disk(test_spacy_filename)

        return train_spacy, valid_spacy, test_spacy, test_data


if __name__ == '__main__':
    annotate_data()


