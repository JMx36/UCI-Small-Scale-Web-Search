from index.merging import parsed_posting, parse_posting_values, split_token
from utils.disk_operations import load_json_from_disk
import math

# weights for scoring
weights = {
    "tf-idf": 0.6,
    "page-rank": 0.2,
    "hits": 0.2
}

# Pre processess the index and calculates some of the scores beforehand
def process_index(index_path, new_index_path, scores_path, total_documents):
    scores = load_json_from_disk(scores_path) # load scores json 
    # query_tokens, query_tf_idf = tokenize(query, {}, total_documents) code for attempted cosine similarity
    with open(new_index_path, "w") as new_file:
        with open(index_path, "r") as file:
            for line in file:
                token, unparsed_posting = split_token(line)
                postings = parsed_posting(unparsed_posting) # get postings in a list format
                new_line = token + ": "
                df = len(postings)
                for pos, posting in enumerate(postings):
                    values = parse_posting_values(posting) # get values of postings like the id and tf score
                    doc_id = values[0]
                    tf_idf = calculate_tf_idf_score(float(values[1]), total_documents, df)
                    total_score = tf_idf
                    values_length = len(values)
                    # Calculate the context scores or extra scoring information
                    if values_length > 2:
                        for index in range(2, values_length):
                            total_score += float(values[index])
                    # cosine_sim = cosine_similarity(query_tf_idf, doc_tf_idf) attempted to add cosine similarity
                    total_score *= weights["tf-idf"]
                    if doc_id in scores:
                        total_score += scores[doc_id]["pagerank"] * weights["page-rank"]
                        total_score += scores[doc_id]["authority"] * weights["hits"]
                    else:
                        total_score += (0.05 * weights["page-rank"]) + (0.05 * weights["hits"])
                    new_line += f'({doc_id}, {total_score})'
                    
                    # we add a , if it nott the last thing element in the list
                    if pos + 1 < len(postings):
                        new_line += ", "
                
                new_file.write(new_line + "\n")
                    
def calculate_tf_idf_score(tf, N, df):
    return tf * math.log(N / df)

