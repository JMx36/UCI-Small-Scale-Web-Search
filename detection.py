import hashlib
from tokenizer.tokenizer import get_tokens, frequency


#initializes the simhash function by computing the binary frequency, hashed value, and making a dictionary for word frequencies.
class Simhash:
    def __init__(self, frequency={}):
        self.word_frequency = frequency
        
        self.cached_bin_frequency = {}
        self.cached_hash_value = -1

        #the size of the simhash value.
        self.hasher: hashlib = hashlib.sha256()
        self.size = (self.hasher.digest_size * 8) + 1
        
    #updates the value of the word frequency dictionary
    def set_frequency(self, frequency):
        self.word_frequency = frequency

    #gets the tokens from the word frequency dictionary
    def get_tokens(self):
        return self.word_frequency.keys()

    #checks if the cashe values are true.
    def do_simhash(self, use_cache=False, use_bin_frequency_cache=False):
        if use_cache: #if they are true then it returns the cached value
            return self.cached_hash_value
        elif use_cache and self.cached_hash_value < 0: #if false and less than zero it returns none.
            return None
        
        if not self.word_frequency:  #determines if there are no word frequencies
            raise Exception("No frequencies in Simhash")
        
        if not use_bin_frequency_cache: #updates the bin friquency cache if false
            self.update_bin_frequency()

        #creates a vector based on the word frequencies
        vector = self._create_vector()
        self.cached_hash_value = self._create_finger_print(vector)

        #returns the cached hash value
        return int(self.cached_hash_value, 2)



    #based on the hash value, the function calculates the binary frequency of the words.
    def update_bin_frequency(self):
        self.cached_bin_frequency = {}
        for word in self.word_frequency:
            self.hasher.update(word.encode('utf-8'))
            hash_value: bytes = self.hasher.hexdigest()
            self.cached_bin_frequency[word] = int(hash_value, 16)
    
    #creates a vector based on the binary frequency in the method above.
    def _create_vector(self):
        vector = []
        for bit_index in range(self.size, -1, -1):
            index_value = 0
            for word, bit_value in self.cached_bin_frequency.items():
                sign = 1 if self._get_bit(bit_value, bit_index) > 0 else -1
                index_value += self.word_frequency[word] * sign
            vector.append(index_value)

        return vector



    #creates a fingerprint based on the vector above, positive are 1, and negative are 0.
    def _create_finger_print(self, vector):    
        finger_print = ""
           
        for number in vector:
            finger_print += "1" if number > 0 else "0"
        
        return finger_print


    #gets/determines bit of exact numbers.
    def _get_bit(self, bit_number, index):
        return (bit_number >> index) & 1


    #turns the hashed values into an integer.
    def __hash__(self) -> int:
        return self.do_simhash(False, False)


    #turns the simhash into a string.
    def __repr__(self) -> str:
        return f"Hash Value = {self.hasher.digest} from Simhash"
    
#calculates the distance between the first and second simhash, and checks if less than the threshhold.
def compare_simhash(simHashA, simHashB, threshold, size):
    return distance_simhash(simHashA, simHashB)/size < threshold

#returns the similarity score between two simhashes, 1 being similar and 0 being not similar.
def similarity_simhash(simHashA, simHashB, size):
    return bin(simHashA ^ simHashB).count("0")/size

#returns the count of the different bits in order to know the distance between them.
def distance_simhash(simHashA, simHashB):
    return bin(simHashA ^ simHashB).count("1")

#returns the sum of all value of the characters.
def checksum(text_data):
    return sum([ord(char) for char in text_data])


if __name__ == "__main__":
    sentence = "Tropical fish include fish found in tropical environments around " + \
                "the world including both freshwater and salt water species"
                
    sentence2 = "Tropical fish include fish found in tropical environments around " + \
                "the world including both freshwater and salt water species"
                
    sentence3 = "1"

    #tokenizes the sentences above, creates a dict for the frequency words, and creates a token count map.
    tokens = get_tokens(sentence)
    frequencies = {}
    frequencies = frequency(tokens)
    
    test_frequency = {"tropical": 2,
                      "found": 1,
                      "world": 1,
                      "freshwater": 1,
                      "species": 1,
                      "fish": 2,
                      "environments": 1,
                      "including": 1,
                      "salt": 1,
                      "include": 1,
                      "around": 1,
                      "both": 1,
                      "water": 1}
    
    cached_bin_frequency = {"tropical": int(b'01100001',2),
                            "found": int(b'00011110', 2),
                            "world": int(b'00101010', 2),
                            "freshwater": int(b'00111111', 2),
                            "species": int(b'11101110', 2),
                            "fish": int(b'10101011', 2),
                            "environments": int(b'00101101', 2),
                            "including": int(b'11000000', 2),
                            "salt": int(b'10110101', 2),
                            "include": int(b'11100110', 2),
                            "around": int(b'10001011', 2),
                            "both": int(b'10101110', 2),
                            "water": int(b'00100101', 2)}
    
    #Hashes value 1
    hasher = Simhash(frequencies)
    value1 = hash(hasher)

    #tokenizes and creates a token count map for sentence 2
    tokens = get_tokens(sentence2)
    frequencies = {}
    frequencies = frequency(tokens)
    hasher.set_frequency(frequencies)

    #hashes the second value or value2
    value2 = hash(hasher)

    #tokenizes and creates a token count map for sentence 3
    tokens = get_tokens(sentence3)
    frequencies = frequency(tokens)
    hasher.set_frequency(frequencies)

    #hashes value3
    value3 = hash(hasher)

    #simhash threshold
    threshold = 0.5

    # simHash.cached_bin_frequency = cached_bin_frequency
    # simHash.update_bin_frequency()
    # print(hash(simHash))

    #checks if value 1 and 2 are similar.
    if not compare_simhash(value1, value2, threshold, hasher.size):
        print("Sentence1 and Sentence2 are very similar")

    #checks if value/sentence 1 and 3 are similar
    if not compare_simhash(value1, value3, threshold, hasher.size):
        print("Sentence1 and Sentence3 are very similar") 

    #checks if value/sentence 2 and 3 are similar.
    if not compare_simhash(value2, value3, threshold, hasher.size):
        print("Sentence2 and Sentence3 are very similar")