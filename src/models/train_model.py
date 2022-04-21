from utils import model_utils
# import spacy_transformers


def train(trained_model_output_dir='../../Models', config_file_path='config.cfg'):
    """
    Function to train a spaCy english pipeline (NER + Tok2Vec) with the help of spaCy Command Line Interface
    :param: str: trained_model_output_dir: directory to save all trained models
    :param: str: config_file_path: path to the config-file used to train the spaCy model
    :return: None
    """
    train_data_path = model_utils.get_spacy_data_path(data_partition='train')
    valid_data_path = model_utils.get_spacy_data_path(data_partition='valid')
    model_to_train_output_directory = model_utils.create_model_path(trained_model_output_dir=trained_model_output_dir)
    model_utils.train_spacy_model(config_filepath=config_file_path,
                                  trained_model_output_dir=model_to_train_output_directory,
                                  train_data_path=train_data_path, valid_data_path=valid_data_path)


if __name__ == '__main__':
    train(config_file_path='config.cfg')
