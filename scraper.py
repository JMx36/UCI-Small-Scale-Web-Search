from urllib.parse import ParseResult, urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
from utils import get_urlhash, normalize
from detection import Simhash, compare_simhash, checksum
from tokenizer.tokenizer import tokenize, frequency, get_tokens_and_frequencies

SIMHASH_THRESHOLD = 0.2  # Threshold for similarity detection to avoid duplicate content

# stopwords_set = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are","aren't", "as", "at", "be", "you", "you", "you've", "your",
#                 "because", "been", "before", "being", "below", "between","both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
#                 "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", 
#                 "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", 
#                 "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
#                 "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
#                 "shouldn't", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", 
#                 "they're", "they've", "this", "those", "through", "too", "under", "to", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
#                 "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you", "yours","yourself","yourselves",
# }

class Scraper:
    def __init__(self, url, content, pages_hash_dict, unique_pages, logger, threshold = 0) -> None:
        self.soup = BeautifulSoup(content, "html.parser")
        self.url = url
        self.logger = logger
        self.pages_hash_dict = pages_hash_dict
        self.unique_pages = unique_pages
        self.page_tokens = None
        self.threshold = threshold if threshold > 0 else SIMHASH_THRESHOLD
        self.simhash_value = 0
        self.checksum_value = 0
        self.outgoing_links_count = 0
    

    def parse_page(self):
        """
        Parses page content to extract texts and hyperlinks
        """
        ###TODO: modified. Added logs to see if we get stuck cuz of tokenization (Josh)
        page_text = self.soup.get_text()  # extract all text from prased HTML
        self.checksum_value = checksum(page_text)
        if self.checksum_value in self.unique_pages: # removed not in, changed to in
            self.logger.warning(f"Detected exact duplicate page. Not scraping, URL- {self.url}")
            return False
        
        context_scores = {}
        CONTEXT_WEIGHTS = {
            'title': 3,
            'h1': 2,
            'strong': 1,
        }
        for context, weight in CONTEXT_WEIGHTS.items():
            for element in self.soup.find_all(context):
                text = element.get_text()
                frequencies = get_tokens_and_frequencies(text)

                for token, freq in frequencies.items():
                    context_scores[token] = context_scores.get(token, 0) + weight * freq

        self.logger.info("Getting tokens")
        self.page_tokens, frequencies = tokenize(page_text, context_scores) # Returns Token objects and frequencies used to create the token object
        # self.logger.info("Generated tokens: %s", self.page_tokens[:10])  # Log the first 10 tokens
        # TODO: commented this for performance
        # self.logger.info("Generated tokens: %s", [token_obj.token for token_obj in self.page_tokens[:10]]) #


        self.logger.info("Finished getting tokens")

        simHasher = Simhash(frequencies)
        self.simhash_value = hash(simHasher)

        #detect similar or duplicate content
        if self.detect_similarity(self.simhash_value, self.pages_hash_dict, simHasher.size, self.threshold):
            self.logger.warning(f"Similar content/close duplicates for {self.url}. No crawling.")
            # empty tokens for prevention purposes
            self.tokens = []
            # we return false if it is a duplicate or similar
            return False

        # we return true if we succesfully parse the page
        return True

    #def detect_similarity(current_hash: int, pages_dict, size, threshold: int = 0.7):
    def detect_similarity(self, current_hash, pages_dict, size, threshold=0.7):
        """
        Detects if current page's content is similar to previously crawled pages
        """
        #for prev_simhash in pages_dict:
        #    if not compare_simhash(current_hash, prev_simhash, threshold, size):
        #        return True
        for prev_simhash in pages_dict:
            if not compare_simhash(current_hash, prev_simhash, threshold, size):
                return True

        return False

    def get_tokens(self) -> list:
        # returns list of tokens extracted from page
        return self.page_tokens
    
    def get_simhash(self) -> int:
        # returns simhash balue of page
        return self.simhash_value
    
    def get_checksum(self) -> int:
        #returns checksum value of page
        return self.checksum_value

    def get_page_info(self):
        #returns tuple containing the page's tokens, simhash value, checksum value, and outgoing links count
        return (self.page_tokens, self.simhash_value, self.checksum_value, self.get_outgoing_links_count())

    def get_outgoing_links_count(self):
        # counts and returns # of outgoing links in page
        if self.outgoing_links_count == 0:
            self.outgoing_links_count = len(self.soup.find_all("a", href='true'))
        
        return self.outgoing_links_count

def extract_fragment(url: ParseResult):
    #remove fragment from URL
    return url._replace(fragment="")


def extract_query(url: ParseResult):
    #remove query string from URL
    return url._replace(query="")


