from threading import Thread, Lock
from utils.config import Config
from utils import get_logger
from utils.disk_operations import load_json_from_disk, load_to_disk
from scraper import extract_fragment
from index.merging import sort_index
from urllib.parse import urlparse
from tokenizer.tokenizer import get_tokens_and_frequencies
from index.posting import Posting
from bs4 import BeautifulSoup
import os
import json


class ConnectivityWorker(Thread):
    def __init__(self, config: Config, main_graph, worker_id, domain_subdir, files =[]):
        self.mini_graph = {}
        self.main_graph = main_graph
        self.config = config
        self.domain_subdir = domain_subdir
        self.worker_id = worker_id
        self.files = files
        self.unload_number = 0
        self.logger = get_logger(f"\ConnectivityGraph\Graph_Worker-{worker_id}")
        # self.index = {}
        super().__init__(daemon=True)
    
    def run(self) -> None:
        domain_path = os.path.join(self.config.corpus_path, self.domain_subdir)
        
        # processing directory
        if not os.path.isdir(domain_path):
            self.logger.error(f"Couldn't find folder at this path- {domain_path}")
            return 

        if not self.files:
            files_in_domain = os.listdir(domain_path)
        else:
            files_in_domain = self.files
        # a = os.listdir(domain_path)
        # self.logger.info(len(a))
        # Iterate over each JSON file within the domain/subdomain directory
         
        for json_filename in files_in_domain:
            try: 
                if not json_filename.endswith(".json"):
                    continue
                    
                json_filepath = os.path.join(domain_path, json_filename)
                
                if not os.path.exists(json_filepath):
                    self.logger.error(f"Couldn't find json file at this path- {json_filepath}")
                    continue
            
                # Read the JSON file and extract HTML content
                self.open_json(json_filepath)
            except IndexError as e:
                self.logger.error(f"Exception: {e}\n, {json_filepath}")
            
        self.logger.info("FINISHED FOLDER")
        
        # Attempted to add code for anchor words index creation
        # if self.index:
        #     new_index = {}
        #     for id, token_set in self.index.items:
        #         new_index[id] = []
        #         for token in token_set:
        #             new_index[id].append(Posting(token, id))
        #     self.index = new_index
        #     self.unload_index()
        self.main_graph.update_graph(self.mini_graph)
        
    def open_json(self, json_filepath):
        with open(json_filepath, 'r') as file:
            json_data = json.load(file)
            html_content = json_data.get('content', '') # where 'content' is the key containing the HTML in the JSON
            url = json_data.get('url', '') # where 'url' is the key containing the url of the webpage
            
            parsed_url = urlparse(url) # parsed url
            parsed_url = extract_fragment(parsed_url) # remove fragment
            clean_url = parsed_url.geturl()
            
            # Add the document to the inverted index using its ID and HTML content
            # was_added = self.add_document(doc_id, html_content, clean_url, json_data.get('encoding', 'UTF-8'))
            
            if self.add_document(html_content, clean_url):
                self.logger.info(f"Added outgoing and incoming links to URL- {clean_url}")
            else:
                self.logger.info(f"Did not add outgoing and incoming links to URL- {clean_url}")
            
    def add_document(self, html_content, clean_url):
        soup = BeautifulSoup(html_content, "html.parser")
        # Check if URL is valid and unique
        if not self.main_graph.is_valid_url(clean_url): 
            return False
        sender_id = self.main_graph.get_id(clean_url)
        links = soup.find_all("a")
        was_added = False
        
        for outgoing_link in links:
            link = outgoing_link.get('href')
            if not link:
                continue
            parsed_url = urlparse(link)  # Parse the URL to handle relative links
            parsed_url = extract_fragment(parsed_url)  # Remove URL fragment
            # Use clean_url for the target URL as well
            clean_url = parsed_url.geturl()
            
            # Ensure target URL is valid and unique
            if not self.main_graph.is_valid_url(clean_url):
                continue
            
            was_added = True
            receiver_id = self.main_graph.get_id(clean_url)
            
            # Attempted to add code for anchor words index creation
            # if receiver_id not in self.index:
            #     self.index[receiver_id] = set()
            
            # token_freq = get_tokens_and_frequencies(outgoing_link.get_text())
            
            # for token in token_freq:
            #     if token not in self.index[receiver_id]:
            #         self.index[receiver_id].add(token)
                
            # Update mini_graph with outgoing and incoming links
            # Outgoing links are added to the sender page
            if sender_id not in self.mini_graph:
                self.mini_graph[sender_id] = {'outgoing': set(), 'incoming': set()}
            self.mini_graph[sender_id]['outgoing'].add(receiver_id)
            
            # Incoming links are added to the receiver page
            if receiver_id not in self.mini_graph:
                self.mini_graph[receiver_id] = {'outgoing': set(), 'incoming': set()}
            self.mini_graph[receiver_id]['incoming'].add(sender_id)
            
        return was_added
    
    def sort_index(self):
        return sort_index(self.index)
    
    def unload_index(self):
        # attempting to unload index of anchor words 
        path = os.path.join(self.config.partial_index_folder, f"Worker{self.worker_id}-{self.unload_number}.txt")
        self.unload_number += 1
        self.sort_index()
        load_to_disk(path, sorted(self.index.items())) 
        self.index = {}