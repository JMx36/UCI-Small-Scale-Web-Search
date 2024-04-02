import os
import json
from threading import Thread
from utils import get_logger, get_urlhash
from scraper import Scraper
from urllib.parse import ParseResult, urlparse
from scraper import extract_fragment
from index.posting import Posting
from index.merging import sort_index, merge_lists
from utils.disk_operations import load_to_disk, getsizeof_in_MB, get_from_disk, remove_file
from utils.config import Config
import re

class IndexWorker(Thread):
    def __init__(self, config: Config, main_indexer, worker_id, domain_subdir, files =[]) -> None:
        self.index = {} # token: list[postings]
        self.total_documents_seen = 0
        self.config: Config = config
        self.domain_subdir = domain_subdir
        self.logger = get_logger(f"Index_Worker-{worker_id}")
        self.worker_id = worker_id
        self.main_indexer = main_indexer
        self.unload_number = 0
        self.max_index_size = int(self.config.MB_max_size)
        self.files = files
        
        self.pages_dict = set()
        self.total_documents_indexed = 0  # Initialize the count
        self.unique_pages = set()
        
        super().__init__(daemon=True)
        
    def run(self):
        domain_path = os.path.join(self.config.corpus_path, self.domain_subdir)
        
        # processing directory
        if not os.path.isdir(domain_path):
            self.logger.error(f"Couldn't find folder at this path- {domain_path}")
            return 

        if not self.files:
            files_in_domain = os.listdir(domain_path)
        else:
            files_in_domain = self.files
        
        # Iterate over json files and open them
        for json_filename in files_in_domain:
            try: 
                # checking that the file is a json file
                if not json_filename.endswith(".json"):
                    continue
                self.logger.info(f"Size of index: {getsizeof_in_MB(self.index):.3f}")
                # checking we don't go over the size limit
                if not self.is_below_size_limit():
                    self.unload_index()
                    
                json_filepath = os.path.join(domain_path, json_filename)
                
                # checking if the json file 
                if not os.path.exists(json_filepath):
                    self.logger.error(f"Couldn't find json file at this path- {json_filepath}")
                    continue
            
                # Read the JSON file and extract HTML content
                self.open_json(json_filepath)
            except Exception as e:
                self.logger.error(f"Exception: {e}\n, {json_filepath}")
            
        self.logger.info("FINISHED FOLDER")
        try:
            # unload index if there is things to unload
            if self.index:
                self.unload_index()
        except Exception as e:
            self.logger.error(f"Exception: {e}\n, {json_filepath}")
             
    def open_json(self, json_filepath):
        with open(json_filepath, 'r') as file:
            json_data = json.load(file)
            html_content = json_data.get('content', '') # where 'content' is the key containing the HTML in the JSON
            url = json_data.get('url', '') # where 'url' is the key containing the url of the webpage
            
            parsed_url = urlparse(url) # parsed url
            parsed_url = extract_fragment(parsed_url) # remove fragment
            clean_url = parsed_url.geturl()
            
            doc_id = self.add_document(html_content, clean_url)
            
            # check if we got a positive doc_id
            if doc_id >= 0:
                self.main_indexer.add_url_id(doc_id, clean_url)
                
    def add_document(self, html_content, url):
        '''
        Adds a document to the inverted index
        
        Parameters:
        - doc_id: An identifier for the document being added
        - html_content: The HTML content of the document
        
        # Example usage:    
        # Loop through each file in the specified folder
        for file in corpus_folder:
            # placeholder
            html_content = "<html><body><p>This is a sample document.</p></body></html>"


            index.add_document(1, html_content)
        '''
        
        url_hash = get_urlhash(url)
        
        # check if page is unique
        if not self.main_indexer.is_unique(url_hash):
            self.logger.error("Did not parse web page. URL is not unique: %s", url)
            return -1
        
        self.main_indexer.add_unique_url(url_hash)

        # Create a Scrapper object on the url we just got
        scrapper = Scraper(url, html_content, self.pages_dict, self.unique_pages, self.logger)

        was_parsed = scrapper.parse_page()

        if not was_parsed:
            self.logger.info("Page parsing failed or detected as duplicate/similar: %s", url)
            return -1
        
        doc_id = self.main_indexer.get_and_increase_id()
        tokens, simhash_value, checksum_value, outgoing_links_count = scrapper.get_page_info()
        
        self.process_tokens(doc_id, tokens, outgoing_links_count)
        # update unique pages and near pages for exact and near duplicate check
        self.add_pages_simhash(simhash_value)          
        self.add_unique_pages_checksum(checksum_value)      
        return doc_id
    
    def process_tokens(self, doc_id, tokens, link_count):
        # make a posting for each token with the necessary information 
        for token_class in tokens:
            token = token_class.token
            posting = Posting(token, doc_id, token_class.frequency, token_class.context_score, outgoing=link_count)

            if token not in self.index:
                self.index[token] = [posting]
            else:
                self.index[token].append(posting)

    def add_pages_simhash(self, value):
        self.pages_dict.add(value)
        
    def add_unique_pages_checksum(self, value):
        self.unique_pages.add(value)

    def is_below_size_limit(self):
        return getsizeof_in_MB(self.index) < self.max_index_size

    def sort_index(self):
        return sort_index(self.index)

    def unload_index(self):
        # Get file path
        path = os.path.join(self.config.partial_index_folder, f"Worker{self.worker_id}-{self.unload_number}.txt")
        # update unload number
        self.unload_number += 1
        # sort index
        # self.sort_index()
        # load index to disk
        load_to_disk(path, sorted(self.index.items())) 
        # reset index for next set of documents
        self.index = {}
        