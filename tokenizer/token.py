class Token:
    def init(self, token, frequency, context_score):
        self.token = token
        self.frequency = frequency
        self.positions = [] #list to store the position of the tokens
        self.n_gram = n_gram  # Indicates whether this is a 1-gram, 2-gram, etc.
        self.is_important = (
            False  # can set this to True based on HTML tagging context
        )
        self.context_score = context_score

    #Add a position to the position list for the token
    def add_position(self, position):
        self.positions.append(position)

    #Mark the token as important
    def mark_important(self):
        self.is_important = True