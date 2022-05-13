from configparser import ConfigParser
from src.utils import model_utils


def parse_spacy_configfile(confi_file_path, epochs, data_dir='Data', use_gpu=False):

    try:
        # Read the config file with the ConfigParser Class
        config = ConfigParser()
        config.optionxform = str
        config.read(confi_file_path)

        # Retrieving latest training & validation data paths
        train_data_path = model_utils.get_spacy_data_path(
            data_partition='train', data_dir=data_dir)
        train_data_path = train_data_path.replace("\\", "/")
        valid_data_path = model_utils.get_spacy_data_path(
            data_partition='valid', data_dir=data_dir)
        valid_data_path = valid_data_path.replace("\\", "/")

        # Make modifications : update train, dev paths é epochs
        config.set(section='paths', option='train',
                   value=f'"{train_data_path}"')
        config.set(section='paths', option='dev', value=f'"{valid_data_path}"')
        config.set(section='training', option='max_epochs', value=str(epochs))

        if use_gpu:
            config.set(section='system', option='gpu_allocator',
                       value='"pytorch"')

        # Saving all modifications to the config file
        with open(f"{confi_file_path}", 'w') as config_file:
            config.write(config_file)
        return f"config file located in {confi_file_path} has been modified with succes"
    except Exception as e:
        print(e)
        return f"Failed to locate config file : {confi_file_path}"


# if __name__ == __name__:
#     config_file = "../docs/config.cfg"
#     # with open(config_file, 'r') as f:
#     #     text = f.read()
#     # print(text)
#     print(parse_spacy_configfile(confi_file_path=config_file,
#                                  epochs=50, use_gpu=False))
