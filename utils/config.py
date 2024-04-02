import re


class Config(object):
    def __init__(self, config, test):
        self.index_folder = config["PROPERTIES"]["INDEX_FOLDER"]
        self.merge_folder = config["PROPERTIES"]["MERGE_FOLDER"]
        self.partial_index_folder = config["PROPERTIES"]["PARTIAL_SAVES_FOLDER"]
        self.sub_index_folder = config["PROPERTIES"]["SUB_INDEX_FOLDER"]
        self.log_folder = config["PROPERTIES"]["LOG_FOLDER"]

        self.summaries_folder = config["PROPERTIES"]["summaries_folder"] 

        self.corpus_folder = config["PROPERTIES"]["CORPUS_FOLDER"]
        self.corpus_test_path = config["PROPERTIES"]["CORPUS_TEST_DEV"]
        self.corpus_dev_path = config["PROPERTIES"]["CORPUS_DEV"]
        
        self.corpus_path = self.corpus_dev_path if not test else self.corpus_test_path

        self.index_file = config["PROPERTIES"]["UNPROCESSED_INDEX"]
        self.main_index = config["PROPERTIES"]["MAIN_INDEX"]
        self.index_of_index = config["PROPERTIES"]["INDEX_OF_INDEX"]
        self.id_json = config["PROPERTIES"]["ID_JSON"]
        self.scores_json = config["PROPERTIES"]["SCORES_JSON"]
        self.connectivity_graph = config["PROPERTIES"]["CONNECTIVITY_GRAPH"]
        self.processed_index = config["PROPERTIES"]["PROCESSED_INDEX"]

        self.max_size = config["SIZE"]["MAX_SIZE"]
        self.MB_max_size = config["SIZE"]["MB_MAX_SIZE"]
        self.LIMIT_LIMIT = config["SIZE"]["LINE_LIMIT"]