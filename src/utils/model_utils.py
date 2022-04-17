import subprocess
import sys
import os
import glob
from datetime import datetime
import json


def load_data(file):
    with open(file, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_spacy_data_path(data_partition, data_dir='../../Data'):
    list_of_files = glob.glob(f'{data_dir}/{data_partition}*.spacy')
    if len(list_of_files) > 0:
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    else:
        return None


def get_last_trained_model(trained_model_output_dir='../../Models'):
    list_of_models = glob.glob(f'{trained_model_output_dir}/*')
    if len(list_of_models) > 0:
        latest_file = max(list_of_models, key=os.path.getctime)
        return latest_file
    else:
        return None


def create_model_path(trained_model_output_dir):
    now = datetime.now()
    date_time = now.strftime("%d%m%Y, %Hh%M")
    date_time = "_".join([_.strip() for _ in date_time.split(",")])
    model_path = f'{trained_model_output_dir}/trained_model_{date_time}'

    return model_path


def train_spacy_model(config_filepath, trained_model_output_dir, train_data_path, valid_data_path):
    """
        Training a spaCy Model using the spaCy 3.0 CLI https://spacy.io/api/cli
    """
    print("Start Of Training")

    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "train",
                    config_filepath,
                    "--output",
                    trained_model_output_dir,
                    "--paths.train",
                    f"{train_data_path}",
                    "--paths.dev",
                    f"{valid_data_path}"])

    print("End Of Training")


def evaluate_spacy_model(trained_model_output_dir, test_data_path, metrics_output):
    """
        Evaluating a trained spaCy Model using the spaCy 3.0 CLI https://spacy.io/api/cli
    """
    print(f"Start Of Evaluating the Model : ** {trained_model_output_dir}/model-best **")

    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "evaluate",
                    f"{trained_model_output_dir}/model-best",
                    f"{test_data_path}",
                    "--output",
                    f"{metrics_output}_model-best_metrics_output.json"])

    print(f"Start Of Evaluating the Model : ** {trained_model_output_dir}/model-last **")

    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "evaluate",
                    f"{trained_model_output_dir}/model-last",
                    f"{test_data_path}",
                    "--output",
                    f"{metrics_output}_model-last_metrics_output.json"])
    print("End Of Evaluation")


if __name__ == '__main__':
    # print(get_spacy_data_path(data_partition='test'))
    print(get_last_trained_model())
