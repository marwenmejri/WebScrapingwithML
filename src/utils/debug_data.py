from utils.config_parser import parse_spacy_configfile

import subprocess
import sys


def debug(base_config_file_path, config_file_path, epochs=5, use_gpu=False):
    """
        Autofill a partial .cfg file with all default values & Create the Config file to train the model using the
        spaCy 3.0 CLI https://spacy.io/api/cli
        Debug the created config.cfg file and show validation errors. The command will create all objects in the tree
        and validate them.
        Analyze, debug and validate your training and development data. Get useful stats, and find problems like
        invalid entity annotations, cyclic dependencies, low data labels and more.
    """

    # Creating config file for cli training
    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "init",
                    "fill-config",
                    f"{base_config_file_path}",
                    f"{config_file_path}"])

    print(parse_spacy_configfile(confi_file_path=config_file_path,
                                 epochs=epochs, use_gpu=use_gpu))

    print(f"Start Of Debugging the config_file : ** {config_file_path} **")
    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "debug",
                    "config",
                    f"{config_file_path}"])

    print("*** End  Of Debugging the Config file **")

    print("*** Start Of Debugging Data : ***")
    subprocess.run([sys.executable,
                    "-m",
                    "spacy",
                    "debug",
                    "data",
                    f"{config_file_path}",
                    "--verbose"])

    print("*** End  Of Debugging data **")

    print("*** End  Of Debugging  **")


# if __name__ == __name__:
#     debug(config_file_path='docs/config.cfg')
