from collections import defaultdict
import nltk
from tokenizer.token import Token
from nltk.tokenize import word_tokenize
import re
from nltk.stem import PorterStemmer


# nltk.download("punkt")

# Initialize the stemmer
stemmer = PorterStemmer()


"""
Tokens: all alphanumeric sequences in the dataset.
• Stop words: do not use stopping while indexing, i.e. use all words, even
the frequently occurring ones.
• Stemming: use stemming for better textual matches. Suggestion: Porter
stemming, but it is up to you to choose.
• Important text: text in bold (b, strong), in headings (h1, h2, h3), and
in titles should be treated as more important than the in other places.
Verify which are the relevant HTML tags to select the important words

"""



#tokenizes the text and determines the frequency
def tokenize(text, context_scores):
    tokens = get_tokens(text)
    token_frequency = frequency(tokens)
    # return create_Tokens(create_tf_scores(token_frequency, len(tokens)), context_scores), token_frequency
    return create_Tokens(create_tf_scores(token_frequency, len(tokens)), context_scores), token_frequency



#use reg expression to find specific characters
def get_tokens(text):
    # tokens = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())
    tokens = re.findall(r'\b[A-Za-z0-9]+\b', text.lower())
    # TODO: maybe include more constraints like word length
   #perform stemming on each token
    return [stemmer.stem(token) for token in tokens if token]


def frequency(tokens):
    # Count the frequency of each token
    freq_map = defaultdict(int)
    for token in tokens:
        freq_map[token] += 1
    return freq_map


#calculate the tf or term frequency of each token
def create_tf_scores(frequency, total_terms):
    tf_scores = {}
    for token in frequency:
        tf_scores[token] = frequency[token]/total_terms
    return tf_scores



def create_Tokens(tf_frequencies, context_scores: dict):  # uses the frequencies map to create a list of Token class
    info = []
    for token, value in tf_frequencies.items():
        info.append(Token(token, value, context_scores.get(token, 0)))
    return info


# Function to generate n-grams
def generate_ngrams(tokens, n=2):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


# Function to add positions to Token objects
def add_positions(token_objects):
    for idx, token_obj in enumerate(token_objects):
        token_obj.add_position(idx)


#tokenizes the text and determines the frequency
def get_tokens_and_frequencies(text):
    tokens = get_tokens(text)
    frequencies = frequency(tokens)
    return frequencies



# Usage: Call this function during the indexing process to tokenize documents, 
# including 1-grams, 2-grams, and 3-grams, and associate positions with 1-grams. 
# this tokenization supports phrase searches and proximity queries.
def enhanced_tokenize(text, context_scores):
    tokens = get_tokens(text)  # Tokenize text to 1-grams
    bigrams = generate_ngrams(tokens, 2)  # Generate 2-grams
    trigrams = generate_ngrams(tokens, 3)  # Generate 3-grams
    all_tokens = tokens + bigrams + trigrams  # Combine all n-grams
    token_frequency = frequency(all_tokens)  # Calculate frequencies

    # Create Token objects for each token
    token_objects = create_Tokens(create_tf_scores(token_frequency, len(all_tokens)), context_scores)
    
    # Add positions to 1-grams
    add_positions([t for t in token_objects if ' ' not in t.token])
    
    return token_objects, token_frequency