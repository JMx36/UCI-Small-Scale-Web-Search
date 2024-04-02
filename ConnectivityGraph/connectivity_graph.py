from utils.disk_operations import load_json_from_disk, save_to_json_disk
from utils.config import Config
from utils import get_logger
from ConnectivityGraph.connectivity_worker import ConnectivityWorker
from threading import Lock
import os
from ConnectivityGraph.page_rank import compute_pagerank  
from ConnectivityGraph.HITS import compute_hits

class ConnectivityGraph(object):
    # initializes conntectiviygraph 
    def __init__(self, config: Config, worker_factory=ConnectivityWorker):
        self.worker_factory = worker_factory
        self.config = config
        self.logger = get_logger('\ConnectivityGraph\Connectivity-Graph')
        self.graph = {}
        self.urls_to_ids = self.get_urls_to_ids(self.config.id_json)
        self.lock = Lock()

    def create_connectivity_graph(self):
        # initiates connnectivity graph then formats and saves to disk
        self.start_async()
        self.join()
        
        # Saving the connectivity graph structure
        for id in self.graph:
            self.graph[id] = [list(self.graph[id]["incoming"]), list(self.graph[id]["outgoing"])]
        save_to_json_disk(self.config.connectivity_graph, self.graph)

    def calculate_scores(self, load):
        # calculates pagerank and HITS scores for graph
        if load:
            self.graph = load_json_from_disk(self.config.connectivity_graph)
        # Directly compute PageRank and HITS scores here
        formatted_graph = self.get_graph_for_pagerank()
        pagerank_scores = compute_pagerank(formatted_graph)
        hub_scores, authority_scores = compute_hits(formatted_graph)
        # Save combined PageRank and HITS scores
        self.save_combined_scores(pagerank_scores, hub_scores, authority_scores, self.config.scores_json)

    def get_urls_to_ids(self, file_path):
        # loads mapping of URLs to IDs from disk
        ids_to_urls = load_json_from_disk(file_path)
        urls_to_ids = {}
        for id, url in ids_to_urls.items():
            urls_to_ids[url] = id        
        return urls_to_ids

    def start_async(self):
        # initiates the async tasks for processing folders and constructing the graph
        folders_list = os.listdir(self.config.corpus_path)
        max_files = 500
        self.workers = []
        worker_id = 0
        for folder in folders_list:
            full_path = os.path.join(self.config.corpus_path, folder)
            if not os.path.isdir(full_path):
                continue
            folder_files = os.listdir(full_path)
            count = len(folder_files)
            # if folder contains more files than threhold divide among multiple workers
            if count > max_files:
                files_group = self.divide_files(folder_files, max_files)
                for group in files_group:
                    # creates new worker for each group of files and starts it
                    self.workers.append(self.worker_factory(self.config, self, worker_id, folder, group))
                    worker_id += 1
                continue
            
            self.workers.append(self.worker_factory(self.config, self, worker_id, folder))
            worker_id += 1
            
        for worker in self.workers:
            worker.start()

    def join(self):
        # waits for all worker tasks to complete 
        for worker in self.workers:
            self.logger.info("Waiting for threads to finish. (JOINING)")
            worker.join()
            self.logger.info("Threads finished. (DONE JOINING)")

    def divide_files(self, files, size):
        # divide list of files into chunks of a specified size
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

    def is_valid_url(self, url):
        # checks if given URL is present in urls_to_ids mapping
        with self.lock:
            return url in self.urls_to_ids

    def get_id(self, url):
        # retrieves the ID corresponding to the given URL from urls_to_ids mapping
        with self.lock:
            return self.urls_to_ids[url]

    def update_graph(self, links_info: dict):
        # updates graph with new link info from processed pages
        with self.lock:
            for id in links_info:
                other_incoming_links, other_outgoing_links = links_info[id]["incoming"], links_info[id]["outgoing"]
                if id in self.graph:
                    self.graph[id]["incoming"].update(other_incoming_links)
                    self.graph[id]["outgoing"].update(other_outgoing_links)
                else:
                    self.graph[id] = {"incoming": other_incoming_links, "outgoing": other_outgoing_links}
    
    def get_graph_for_pagerank(self):
        # Prepares the connectivity graph for PageRank calculation
        graph_for_pagerank = {}
        for page_id, links in self.graph.items():
            graph_for_pagerank[page_id] = {'incoming': links[0], 'outgoing': links[1]}
        return graph_for_pagerank
    
    def save_combined_scores(self, pagerank_scores, hub_scores, authority_scores, output_file):
        # Combining PageRank, Hub, and Authority scores into one structure
        combined_scores = {page: {'pagerank': pagerank_scores[page], 'hub': hub_scores[page], 'authority': authority_scores[page]} for page in self.graph}
        save_to_json_disk(output_file, combined_scores)
        self.logger.info("Combined PageRank and HITS scores saved to {}".format(output_file))


if __name__ == "__main__":
    config = Config()
    c = ConnectivityGraph(config)
    # c.create_connectivity_graph()
    c.calculate_scores(True)
