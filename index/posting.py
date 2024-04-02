class Posting:
    # Initialize Posting object and TF-IDF score set to 0 initially.
    def __init__(self, token, doc_id, frequency, context_score = 0, outgoing=0, incoming=0, anchor_text=""):
        self.doc_id = doc_id
        self.token = token  # The specific term or token in the document
        # self.url = url  # The URL of the document, useful for web search results
        self.frequency = frequency 
        self.tf_idf_score = 0  # TF-IDF score, to be calculated during search
        
        self.outgoing_links = outgoing  # count of outgoing links from the document
        self.incoming_links = incoming  # incoming links to the doc
        self.anchor_text = anchor_text  # Anchor text from hyperlinks pointing to the document
        self.context_score = context_score
        #self.positions = positions if positions is not None else [] # store positions

    def add_position(self, position):
    # Add a position where the term occurs within a document
        self.positions.append(position)

    def get_positions(self):
        # Return the list of positions where the term occurs within the document
        return self.positions
    
    # Method to update the TF-IDF score for this posting, using the IDF value provided during search
    def update_tf_idf_score(self, idf):
        self.tf_idf_score = self.frequency * idf # Calculate TF-IDF score

    def add_incoming(self, number = 1):
        self.incoming_links += number

    def add_outgoing(self, number = 1):
        self.add_outgoing += number

    def set_outgoing(self, number):
        self.outgoing_links = number

    def set_incoming(self, number):
        self.incoming_links = number

    def get_score(self):
        # we return frequency score but we need to come up with a better scoring system
        return self.tf_idf_score

    def __lt__(self, other: object)-> bool:
        return self.get_id() < other.get_id()
    
    def __eq__(self, other: object) -> bool:
        return self.get_id() == other.get_id()
    
    def get_id(self):
        return self.doc_id

    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, state):
        self.__dict__ = state

    def __hash__(self) -> int:
        return self.doc_id
    
    def __repr__(self) -> str:
        return f"({self.doc_id}, {self.frequency}, {self.context_score})"