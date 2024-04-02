from index.worker import IndexWorker
from utils import get_logger
from utils.disk_operations import load_to_disk, get_from_disk, getsizeof_in_bytes, remove_file, save_to_json_disk
from utils.config import Config
import os
from typing import Dict
from index.merging import merge_lists, sort_index, merge_indexes
from threading import RLock


class InvertedIndex(object):
    def __init__(self, config: Config, worker_factory=IndexWorker):
        self.index: Dict[str, Dict] = dict() # initialize the index as an empty dictionary
        self.config = config
        self.worker_factory = worker_factory
        self.logger = get_logger("Inverted-Index")
        self.save = None
        self.total_index_documents = 0
        self.total_documents_indexed = 0  # Initialize the document count
        self.lock = RLock()
        self.ids_to_urls: Dict[int, str]= {}
        self.urls_to_ids: Dict[str, int]= {}
        self.unique_pages = set()

    def start_async(self): 
        folders_list = os.listdir(self.config.corpus_path)
        max_files = 500
        self.workers = []
        worker_id = 0
        for folder in folders_list:
            full_path = os.path.join(self.config.corpus_path, folder)
            if not os.path.isdir(full_path):  # Skip if it's not a directory
                self.logger.warning(f"Skipping path {full_path} because it is not a directory")
                continue
            folder_files = os.listdir(full_path)
            count = len(folder_files)
            # if the files inside the directory is higher than the max file count then we split it the folder into chunks
            if count > max_files:
                # Divide files
                files_group = self.divide_files(folder_files, max_files)
                for group in files_group:
                    self.workers.append(self.worker_factory(self.config, self, worker_id, folder, group))
                    worker_id += 1
                continue
            
            self.workers.append(self.worker_factory(self.config, self, worker_id, folder))
            worker_id += 1
            
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()
        save_to_json_disk(self.config.id_json, self.ids_to_urls)
        # self.index_merging()
        self.log_info()

    def join(self):
        for worker in self.workers:
            self.logger.info("Waiting for threads to finish. (JOINING)")
            worker.join()
            self.logger.info("Threads finished. (DONE JOINING)")
        
    def divide_files(self, files, size):
        # Divide the files into chunks of the specified size
        num_parts = len(files) // size
        remainder = len(files) % size
        start = 0
        parts = []
        for _ in range(num_parts):
            end = start + size
            parts.append(files[start:end])
            start = end
        if remainder:
            parts.append(files[start:])
        return parts
    
    def index_merging(self):
        # Function that calls the merging process of our index
        # Creates the intial merging files from PartialIndexSaves
        # then merges those files until there is one left
        
        merged_files_count = self.create_merge_files(self.config.partial_index_folder)    
        self.final_merging(self.config.merge_folder, merged_files_count)    
        # print(merged_files_count)
        files = os.listdir(self.config.merge_folder) 
        if len(files) > 1:
            self.logger.error(f"There is more than one file left to merge at the end of the process. This should not happen")
            return
        if files:
            merged_index_path = os.path.join(self.config.merge_folder, files[0])
            merge_indexes(self.config.index_file, merged_index_path)        
    
    def create_merge_files(self, folder_path):
        # Creates the initial merge files from the partial indexes files from PartialIndexSaves folder
        partial_indexes = os.listdir(folder_path)
        number_to_merge = 2
        files_to_merge = []
        merge_file_number = 0
        for partial_index in partial_indexes:
            file_path = os.path.join(folder_path, partial_index)       
            files_to_merge.append(file_path)
            if len(files_to_merge) < number_to_merge:
                continue
            merged_file_path = os.path.join(self.config.merge_folder, f"Merged_file_{merge_file_number}.txt")
            merge_indexes(files_to_merge[0], files_to_merge[1], merged_file_path)
            merge_file_number += 1
            files_to_merge.clear()
        
        if files_to_merge and merge_file_number > 0:
            last_file_merged = os.path.join(self.config.merge_folder, f"Merged_file_{merge_file_number - 1}.txt")
            new_file_merged = os.path.join(self.config.merge_folder, f"Merged_file_{merge_file_number}.txt")
            merge_indexes(files_to_merge[0], last_file_merged, new_file_merged)
            merge_file_number += 1
            remove_file(last_file_merged)
        
        return merge_file_number
    
    def final_merging(self, folder_path, count):
        # Functions merges the files inside Merges folder by merging two files at the same time
        # then removing them. Repeating this process until there is only one file left.
        number_to_merge = 2
        files_to_merge = []
        merged_files = os.listdir(folder_path)
        self.logger.info(str(merged_files))
        left_to_merge = len(merged_files)
        merge_file_number = count
        # loop until there is only one file left
        while left_to_merge > 1:
            left_to_merge = 0
            for partial_index in merged_files:
                file_path = os.path.join(folder_path, partial_index)       
                files_to_merge.append(file_path)
                if len(files_to_merge) < number_to_merge:
                    continue
                merged_file_path = os.path.join(self.config.merge_folder, f"Merged_file_{merge_file_number}.txt")
                # Merges indexes
                merge_indexes(files_to_merge[0], files_to_merge[1], merged_file_path)
                merge_file_number += 1
            
                self.logger.info(f"files_removed: {str(files_to_merge)}")
                for file in files_to_merge:
                    remove_file(file)
                    
                files_to_merge.clear()
            
            if files_to_merge:
                files_to_merge.clear()    

            # there would be files in files_to_merge
            merged_files = os.listdir(folder_path)
            # self.logger.info(str(merged_files))
            left_to_merge = len(merged_files)
            
    def get_and_increase_id(self, value = 1):
        with self.lock:
            # Increment the document count by the given value (default is 1)
            self.total_documents_indexed += value #
            return self.total_documents_indexed
            
    def log_info(self):        
        # self.logger.info(
        #     f"# indexed documents: {self.total_documents_indexed}\n" + \
        #     f"# of unique words: {len(self.save)}\n" + \
        #     f"size of index on disk: {os.path.getsize(self.config.index_file)}")
        self.logger.info(f"# of unique documents: {self.total_documents_indexed}")

    def get_total_documents_indexed(self):
        return self.total_documents_indexed
    
    def add_url_id(self, id, url):
        # adds URL id to ids and urls dictionary
        with self.lock:
            if id in self.ids_to_urls:
                self.logger.error(f"Trying to add a doc id already added {id}")
                return
            
            self.ids_to_urls[id] = url
            self.urls_to_ids[url] = id
                
    def get_id_from_url(self, url):
        # gets the id from url
        with self.lock:
            return self.urls_to_ids[url]

    def is_unique(self, url_hash):
        with self.lock:
            return not url_hash in self.unique_pages
        
    def add_unique_url(self, url_hash):
        with self.lock:
            self.unique_pages.add(url_hash)
            
if __name__ == "__main__":
    pass
    