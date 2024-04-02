import time
from tokenizer.tokenizer import get_tokens
from utils.disk_operations import load_json_from_disk
from index.merging import parsed_posting, parse_posting_values, get_equal_postings_id_set
from index.index_of_index import fetch_index_data, parse_index_of_index
from utils.config import Config
from configparser import ConfigParser, ExtendedInterpolation

class SearchEngine:
    def __init__(self, config: Config, logger, return_count=5):
        # The inverted index created during the indexing process
        self.id_to_url = load_json_from_disk(config.id_json)  # The dictionary mapping doc IDs to URLs
        self.index_of_index = parse_index_of_index(config.index_of_index) # Dictionary mapping tokens to their place in the index file
        self.config = config
        # self.total_documents = len(self.id_to_url)
        self.logger = logger
        self.return_count = return_count

    def parse_postings(self, unparsed_postings):
        all_parsed_postings = []
        for posting in unparsed_postings:
            _parsed_posting = parsed_posting(posting)
            all_parsed_postings.append((len(_parsed_posting), _parsed_posting))

        return all_parsed_postings

    def merge_postings(self, tuple_postings: list):
        # print(tuple_postings)
        tuple_posting = tuple_postings[0]
        current_posting = tuple_posting[1]
        for index in range(1, len(tuple_postings)):
            # print(current_posting)
            if not current_posting:
                return set()
            current_posting = get_equal_postings_id_set(current_posting, tuple_postings[index][1])
        
        return set([id_text.split(",")[0] for id_text in current_posting])
            
    def search(self, query):
        # Tokenize the query and extract token strings
        tokens = get_tokens(query) 

        # Retrieve postings lists and convert to document ID sets
        start_time = time.time()
        self.logger.info("Starting searching postings")
        #TODO: move time operations to calculate the time it takes to fecth the data and parse the postings
        postings = fetch_index_data(self.config.main_index, self.index_of_index, tokens)
        self.logger.info(f"Fetched index data in {(time.time() - start_time) * 1000:.4f} ms")
        if not postings:
            raise Exception("NO POSTINGS!!!")
        parsed_postings_list = self.parse_postings(postings)
        ordered_postings_list = sorted(parsed_postings_list, key=lambda x: x[0])
        common_doc_ids = self.merge_postings(ordered_postings_list)
        # Store postings per token
        self.logger.info(f"Finished collecting for postings in {(time.time() - start_time) * 1000:.4f} ms")
        # Calculate TF-IDF scores for common documents
        self.logger.info(f"Common doc ids: {len(common_doc_ids)}")
        doc_scores = self.compute_doc_scores(common_doc_ids, ordered_postings_list)
        
        # Return the sorted list of document IDs [with urls] and scores
        return [(doc_scores[index][0], self.id_to_url[doc_scores[index][0]], doc_scores[index][1])
            for index in range(min(self.return_count, len(doc_scores)))
        ]

    def compute_doc_scores(self, common_doc_ids, ordered_postings_list):
        # Find intersection of document ID sets for common documents
        document_score = {}
        for tuple_postings_list in ordered_postings_list:
            for posting in tuple_postings_list[1]:
                values = parse_posting_values(posting)
                doc_id = values[0]
                if doc_id in common_doc_ids:
                    term_doc_score = values[1]
                    total_score = document_score.get(doc_id, 0) + float(term_doc_score)
                    document_score[doc_id] = total_score 
                    
        # Sort documents by TF-IDF scores in descending order            
        return sorted(document_score.items(), key=lambda doc_info: -doc_info[1])


def test_merge_postings(engine: SearchEngine):
    postings = [
                '(44, 4.780944480973242), (72, 40.24755584778594), (103, 4.780944480973242), (165, 4.780944480973242), (238, 9.561888961946485), (312, 4.780944480973242), (407, 14.342833442919726), (432, 4.780944480973242), (514, 4.780944480973242), (528, 21.12377792389297), (554, 4.780944480973242), (556, 4.780944480973242), (661, 4.780944480973242), (664, 9.561888961946485), (665, 65.15227825265215), (724, 9.561888961946485), (754, 9.561888961946485), (863, 4.780944480973242), (884, 4.780944480973242), (906, 4.780944480973242), (1009, 4.780944480973242), (1056, 4.780944480973242), (1343, 9.561888961946485), (1347, 9.561888961946485), (1352, 4.780944480973242), (1361, 9.561888961946485), (1374, 4.780944480973242), (1405, 4.780944480973242), (1456, 4.780944480973242), (1509, 4.780944480973242), (1611, 4.780944480973242), (1671, 4.780944480973242), (1681, 4.780944480973242), (1733, 4.780944480973242), (1859, 19.12377792389297), (1869, 14.342833442919726), (1878, 4.780944480973242), (1954, 4.780944480973242), (1965, 6.780944480973242), (1977, 4.780944480973242), (1985, 4.780944480973242), (2133, 4.780944480973242), (2143, 4.780944480973242), (2171, 9.561888961946485), (2175, 4.780944480973242), (2326, 4.780944480973242), (2425, 4.780944480973242), (2442, 4.780944480973242), (2462, 12.561888961946485), (2500, 4.780944480973242), (2543, 4.780944480973242), (2570, 4.780944480973242), (2615, 4.780944480973242), (2899, 14.561888961946485), (2919, 4.780944480973242), (2945, 4.780944480973242), (2954, 52.590389290705666), (2974, 4.780944480973242), (2989, 9.561888961946485), (3211, 4.780944480973242), (3227, 9.561888961946485), (3571, 23.904722404866213), (3595, 4.780944480973242), (3765, 4.780944480973242), (3887, 4.780944480973242), (3919, 9.561888961946485), (3963, 9.561888961946485), (3972, 65.15227825265215), (4094, 4.780944480973242), (4223, 4.780944480973242), (4257, 4.780944480973242), (4302, 9.561888961946485), (4318, 4.780944480973242), (4590, 14.342833442919726), (4644, 17.342833442919726), (4805, 9.561888961946485), (4824, 4.780944480973242), (4980, 4.780944480973242), (5083, 4.780944480973242), (5136, 4.780944480973242), (5156, 23.904722404866213), (5189, 4.780944480973242), (5249, 9.561888961946485), (5368, 9.561888961946485), (5467, 4.780944480973242), (5550, 4.780944480973242), (5691, 4.780944480973242), (5777, 4.780944480973242), (5874, 4.780944480973242), (5901, 4.780944480973242), (6019, 4.780944480973242), (6134, 4.780944480973242), (6289, 4.780944480973242), (6429, 4.780944480973242), (6431, 4.780944480973242), (6454, 4.780944480973242), (6508, 9.561888961946485), (6521, 9.561888961946485), (6567, 9.561888961946485), (6595, 9.561888961946485), (6658, 4.780944480973242), (6673, 4.780944480973242), (6773, 4.780944480973242), (6832, 4.780944480973242), (6953, 9.561888961946485), (7049, 9.561888961946485)'
                '(72, 1), (176, 1), (209, 6), (229, 1), (367, 3), (587, 1), (687, 2), (738, 1), (836, 7), (870, 5), (1072, 1), (1262, 1), (1390, 1), (1394, 4), (1486, 1), (1556, 4), (1581, 4), (1664, 2), (2067, 1), (2276, 3), (2579, 1), (2668, 1), (2861, 5), (3020, 1), (3061, 8), (3279, 4), (3419, 1), (3427, 1), (3514, 2), (3738, 6), (3758, 16), (3886, 3), (4030, 6), (4597, 3), (4620, 2), (4732, 2), (4844, 3), (4859, 1), (5001, 1), (5123, 2), (5145, 1), (5419, 2), (5734, 1), (5773, 3), (6288, 2), (6408, 17), (6482, 1), (6547, 1), (6592, 4), (6628, 2), (6714, 1), (6915, 3), (7093, 2), (7572, 3), (8040, 2), (8168, 3), (8187, 1), (8343, 3), (8459, 1), (8461, 1), (8491, 2), (8513, 1), (8759, 3), (9243, 1), (9324, 1), (9345, 1), (9523, 4), (9660, 1), (9975, 1), (10163, 1), (10215, 2), (10296, 1), (10425, 4), (10869, 1), (11060, 1), (11087, 1), (11091, 10), (11229, 4), (11277, 1), (11473, 4), (11501, 7), (11661, 6), (11772, 3), (11780, 7), (11796, 1), (11808, 1), (11988, 3), (12226, 1), (12535, 1), (13242, 1), (13841, 1), (14324, 1), (14344, 3), (14585, 1), (14649, 6), (14674, 1), (14873, 1), (14893, 5), (15054, 1), (15130, 1), (15524, 7), (15843, 2), (15939, 1), (16185, 1), (16251, 3), (16867, 6), (16976, 1), (17410, 5), (17522, 1), (17745, 1), (17845, 1), (17973, 1), (18028, 3), (18053, 1), (18114, 1), (18303, 4), (18325, 2), (18554, 3), (18693, 2), (19209, 9), (19318, 4), (19680, 1), (19826, 3), (20178, 1), (20468, 9), (20477, 1), (20484, 1), (20560, 1), (20646, 1), (20786, 1), (21911, 1), (22277, 1), (22852, 1), (23250, 1), (23291, 1), (23430, 2), (23474, 1), (23502, 1), (23854, 1), (24264, 1), (24427, 1), (24907, 1), (24908, 1), (24995, 17), (25055, 2), (25122, 1), (25127, 1), (25182, 1), (25697, 1), (25858, 3), (25947, 1), (25959, 1), (26178, 5), (26232, 1), (27309, 2), (27394, 1), (27684, 11), (27707, 1), (28596, 1), (29735, 3), (29810, 5), (30131, 1), (30211, 3), (30444, 1), (30623, 1), (30710, 4), (30781, 1), (30939, 1), (31295, 1), (31605, 5), (31869, 6), (32648, 3), (33336, 2), (33458, 7), (33608, 1), (33728, 3), (33744, 2), (33880, 1), (33952, 5), (34031, 6), (34072, 1), (34282, 1), (34394, 1), (34681, 1), (34978, 1), (35047, 1), (35238, 4), (35519, 6), (35647, 1), (36150, 3), (36200, 4), (36770, 1), (36861, 3), (37109, 1), (37181, 1), (37249, 2), (37456, 1), (37620, 5), (37927, 6), (38102, 1), (38345, 3), (38510, 1), (38607, 20), (38645, 2), (39464, 5), (39768, 3), (40172, 3), (40437, 6), (40841, 1), (41005, 1), (41818, 1), (42254, 7), (42387, 1), (42474, 1), (42521, 2), (43661, 1), (44194, 2), (44206, 4), (44802, 1), (45516, 1), (46033, 4), (47486, 1), (47660, 5), (47904, 1), (48780, 12), (48796, 3), (49051, 3), (49296, 5), (49858, 1), (49917, 5), (50370, 1), (50652, 2), (50742, 3), (51249, 1)'
        ]
    # postings = ['(2, 5), (4, 5)', '(4, 5)']
    
    parsed_postings_list = engine.parse_postings(postings)
    ordered_postings_list = sorted(parsed_postings_list, key=lambda x: x[0])
    # print(ordered_postings_list)
    common_doc_ids = engine.merge_postings(ordered_postings_list)
    # print(common_doc_ids)
    print(engine.compute_doc_scores(common_doc_ids, ordered_postings_list))

if __name__ == "__main__":
    cparser = ConfigParser(interpolation=ExtendedInterpolation())
    cparser.read("config.ini")
    config = Config(cparser, False)
    # Load the inverted index and the ID-to-URL mapping
    #TODO: questions
    # What is the limit that our index of index can be before we can't load it into memory anymore?

    # Initialize SearchEngine with the loaded index
    search_engine = SearchEngine(config, 30)
    test_merge_postings(search_engine)
    # print(fetch_index_data(config.index_file, parse_index_of_index(config.index_of_index), ["acm"]))
    # search loop
    # while True:
    #     query = input("Enter a search query (or type 'exit' to stop): ").strip()
    #     if query.lower() == "exit":
    #         print("Exiting the search engine.")
    #         break

    #     # Perform the search with the user's query and print the results
    #     results = search_engine.search(query)
    #     print(f"Results for '{query}': {results}")
