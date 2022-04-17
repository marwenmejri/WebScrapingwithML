import spacy
import json
import glob
import os
from spacy.training import offsets_to_biluo_tags
from src.utils import model_utils
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot
import numpy


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def search_for_last_created_json_testdata(data_dir='../../Data'):
    list_of_files = glob.glob(f'{data_dir}/test*.json')
    if len(list_of_files) > 0:
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    else:
        return None


def make_formal_test():
    test_data_path = search_for_last_created_json_testdata()
    test_data = load_data(test_data_path)
    docs = test_data
    # Load the Traind Model
    last_trained_model_path = model_utils.get_last_trained_model()
    model_name = last_trained_model_path.split("\\")[-1]
    nlp = spacy.load(f"{last_trained_model_path}/model-last")

    def get_cleaned_label(label: str):
        if "-" in label:
            return label.split("-")[1]
        else:
            return label

    def create_total_target_vector(docs):
        target_vector = []
        for doc in docs:
            print(doc)
            new = nlp.make_doc(doc[0])
            entities = doc[1]["entities"]
            bilou_entities = offsets_to_biluo_tags(new, entities)
            final = []
            for item in bilou_entities:
                final.append(get_cleaned_label(item))
            target_vector.extend(final)
        return target_vector

    def create_prediction_vector(text):
        return [get_cleaned_label(prediction) for prediction in get_all_ner_predictions(text)]

    def create_total_prediction_vector(docs: list):
        prediction_vector = []
        for doc in docs:
            prediction_vector.extend(create_prediction_vector(doc[0]))
        return prediction_vector

    def get_all_ner_predictions(text):
        doc = nlp(text)
        entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
        bilou_entities = offsets_to_biluo_tags(doc, entities)
        return bilou_entities

    def get_model_labels():
        labels = list(nlp.get_pipe("ner").labels)
        labels.append("O")
        return sorted(labels)

    def get_dataset_labels():
        return sorted(set(create_total_target_vector(docs)))

    def generate_confusion_matrix(docs):
        classes = sorted(set(create_total_target_vector(docs)))
        y_true = create_total_target_vector(docs)
        y_pred = create_total_prediction_vector(docs)
        print(y_true)
        print(y_pred)
        return confusion_matrix(y_true=y_true, y_pred=y_pred, labels=classes)

    generate_confusion_matrix(docs)

    def plot_confusion_matrix(docs, classes, normalize=False, cmap=pyplot.cm.Blues):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """

        title = 'Confusion Matrix, for SpaCy NER'

        # Compute confusion matrix
        cm = generate_confusion_matrix(docs)
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, numpy.newaxis]

        fig, ax = pyplot.subplots()
        im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
        ax.figure.colorbar(im, ax=ax)
        # We want to show all ticks...
        ax.set(xticks=numpy.arange(cm.shape[1]),
               yticks=numpy.arange(cm.shape[0]),
               # ... and label them with the respective list entries
               xticklabels=classes, yticklabels=classes,
               title=title,
               ylabel='True label',
               xlabel='Predicted label')

        # Rotate the tick labels and set their alignment.
        pyplot.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
        fig.tight_layout()
        pyplot.savefig(f"../reports/{model_name}_conf_matrix.png")
        pyplot.show()
        return cm, ax, pyplot

    plot_confusion_matrix(docs, classes=get_dataset_labels(), normalize=False)


if __name__ == "__main__":
    make_formal_test()
