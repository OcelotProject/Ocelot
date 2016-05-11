from .io import extract_directory
from .transforms import relabel_global_to_row
import pickle


class SystemModel(object):
    def __init__(self, data_path, config=None):
        config = config or {}
        # TODO: Parse config
        data = extract_directory(data_path)
        log = None # Setup
        self.apply_system_model(config, data, log)

    def apply_system_model(self, config, data, log):
        # TODO: Interpret config
        for transform in [relabel_global_to_row]:
            data = self.apply_transform(transform, data, log)

    def apply_transform(self, transform, data, log):
        print("Applying transform {}".format(transform.__name__))
        data = transform(data)
        with open("dump.pickle", "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
