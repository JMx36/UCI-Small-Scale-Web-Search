# search_launch.py
import sys
from search2 import SearchEngine
import time
from configparser import ConfigParser, ExtendedInterpolation
from utils.config import Config
from utils import get_logger

def main(config):
    # Load the inverted index and ID-to-URL mapping
    # Initialize the SearchEngine with the loaded index and ID-to-URL mapping
    logger = get_logger("Engine")
    search_engine = SearchEngine(config, logger, 5)
    print("Search Engine. Type 'exit' to exit search engine.")

    while True:
        query = input("Enter query: ").strip()
        if query.lower() == "exit":
            logger.info("Goodbye.")
            break
        #print("Processing query...")
        start_time = time.time()  # Start timing the query processing
        results = search_engine.search(query)
        end_time = time.time()  # End timing the query processing

        response_time = end_time - start_time  # Calculate the response time
        logger.info(f"Query processed in {response_time * 1000:.4f} ms")

        if results:
            logger.info(f"'{query}' results (Top 5): ")
            # for doc_id, url, score in results:
            for doc_id, url, score in results:  # modified to return only top 5
                logger.info(f"Document ID: {doc_id}, URL: {url}, Score: {score}")
                
        else:
            logger.info("No results found.")


if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    cparser = ConfigParser(interpolation=ExtendedInterpolation())
    cparser.read("config.ini")
    config = Config(cparser, False)

    main(config)
