from index.inverted_index import InvertedIndex
from argparse import ArgumentParser
from configparser import ConfigParser, ExtendedInterpolation
from ConnectivityGraph.connectivity_graph import ConnectivityGraph
from utils.config import Config
from utils.disk_operations import clear_folder, remove_file, create_folder
from index.index_of_index import create_index_of_index
from index.process_index import process_index
from utils.disk_operations import load_json_from_disk
import os


def main(test, config_file, restart, merge_restart, log_restart):
    """
    Main function to process HTML files from a specified folder and add them to the inverted index.
    
    Parameters:
    - folder: Path to the folder containing HTML files to be indexed.
    """
    cparser = ConfigParser(interpolation=ExtendedInterpolation())
    cparser.read(config_file)
    config = Config(cparser, test)
    if restart:
        restart_program(config)
    if merge_restart:
        clear_folder(config.merge_folder)
    
    if log_restart:
        clear_folder(config.log_folder)    
        
    index = InvertedIndex(config)
    index.start()
    index.index_merging()
    
    # These 3 lines are for the connectivity graph which should only be used after you have id_json file
    conn_graph = ConnectivityGraph(config)
    conn_graph.create_connectivity_graph()
    conn_graph.calculate_scores(True)
    
    total_documents = len(load_json_from_disk(config.id_json))
    process_index(config.index_file, config.main_index, config.scores_json, total_documents)
    create_index_of_index(config.main_index, config.index_of_index, 5000)

def restart_program(config: Config):
    if os.path.exists(config.partial_index_folder):
        clear_folder(config.partial_index_folder)
    else:
        create_folder(config.partial_index_folder)
    
    if os.path.exists(config.merge_folder):
        clear_folder(config.merge_folder)
    else:
        create_folder(config.merge_folder)

    if os.path.exists(config.index_folder):
        if not os.path.exists(config.sub_index_folder):
           create_folder(config.sub_index_folder)
        else:
           clear_folder(config.sub_index_folder)
        clear_folder(config.index_folder)
    else:
        create_folder(config.index_folder)
        create_folder(config.sub_index_folder)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", type=str, default=False) # Add command line argument for the folder
    parser.add_argument("--config_file", type=str, default="config.ini") # Add command line argument for the folder
    parser.add_argument("--restart", type=bool, default=False) # Add command line argument for the folder
    parser.add_argument("--merge_restart", type=bool, default=False) # Add command line argument for the folder
    parser.add_argument("--log_restart", type=bool, default=False) # Add command line argument for the folder
    args = parser.parse_args()
    main(args.test, args.config_file, args.restart, args.merge_restart, args.log_restart)
