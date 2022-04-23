from src.utils import model_utils
from src.utils import confusion_matrix_utils


def evaluate():
    test_data_path = model_utils.get_spacy_data_path(data_partition='test')
    last_trained_model_path = model_utils.get_last_trained_model()
    model_name = last_trained_model_path.split('\\')[-1]
    model_utils.evaluate_spacy_model(trained_model_output_dir=last_trained_model_path,
                                     test_data_path=test_data_path, metrics_output=f"src/reports/{model_name}")
    confusion_matrix_utils.make_formal_test()


if __name__ == '__main__':
    evaluate()
