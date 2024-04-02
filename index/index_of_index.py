import json
from utils.disk_operations import getsizeof_in_MB, getsizeof_in_bytes
from index.merging import split_token, parsed_posting

def create_index_of_index(index_path, new_index_path, unload_threshold):
    # creates an index of index using the token as the key and byteoffset as values
    with open(new_index_path, 'w', encoding="utf-8") as new_index_file:
        with open(index_path, 'r', encoding="utf-8") as index_file:
            lines_txt = ""
            bytes_offset = 0
            for line in index_file:                
                token, _ = split_token(line)
                
                # give offset value to token
                lines_txt += f"{token}: {bytes_offset}\n"
                 # we add an extra space to move to the start of the next line, or else we would be at the end of the line
                bytes_offset += len((line+" ").encode('utf-8'))
                if getsizeof_in_MB(lines_txt) > unload_threshold:
                    new_index_file.write(lines_txt)
            
            if lines_txt:
                new_index_file.write(lines_txt)
                
# function for adjusting line lenght but it is not used in the program
def adjust_line_length(line, line_limit):
    line_break = "-\n"
    new_line_character = "\n"
    line_length = len(line)
    line = line.rstrip()
    if line_length < line_limit:
        return pad_line(line, line_limit - len(new_line_character)) + "\n"
    
    start_pos = line_limit - len(line_break)
    correct_line = line[:start_pos] + "-\n" # we add a - at the end to know the line continues. We substract 3 cuz there are three characters we adding
    left_over = line_length - start_pos  
    # print(line_length)
    # print(left_over)
    while left_over > 0:    
        # print(left_over - len(line_break))
        end_pos = start_pos + min(line_limit - len(line_break), left_over + len(line_break))
        # print(end_pos)
        next_line = line[start_pos: end_pos]
        next_line_length = len(next_line)
        
        if next_line_length < line_limit - len(line_break):
            correct_line += pad_line(next_line, line_limit - len(new_line_character)) + "\n"
            break
        
        next_line += line_break
        correct_line += next_line
        
        left_over = line_length - end_pos
        start_pos = end_pos
        
    return correct_line
    

def pad_line(line, desired_length):
    # function for padding the line
    return line + ' ' * (desired_length - len(line))     

    
def parse_index_of_index(file_path):
    # parses index of index file into a dictionary to be used
    index_dictionary = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            token, byte_offset = line.strip().split(':')
            token = token.strip()
            byte_offset = int(byte_offset.strip())
            index_dictionary[token] = byte_offset
                
    return index_dictionary


def fetch_index_data(file_path, index_of_index, tokens: list):
    # gets the the posting line of the token using the index of index for fast retrieval
    with open(file_path, 'r', encoding="utf-8") as file:
        postings = []
        for token in tokens:
            file.seek(index_of_index[token], 0)
            postings.append(file.readline())
    return postings


if __name__ == "__main__":
    # line = "0: (1, 3), (3, 1), (6, 15), (12, 4), (14, 1), (15, 1), (16, 5), (17, 9), (18, 1), (20, 15), (22, 1), (24, 1), (25, 5), (26, 1), (29, 1), (37, 17), (53, 1), (57, 3), (58, 3), (60, 1), (67, 3), (72, 7), (73, 1), (77, 4), (79, 1)"

    # print(adjust_line_length(line, 200))
    create_index_of_index("indexes\main_index.txt", "index_of_index.txt", 5000)
    
    # index_dictionary = parse_index_of_index("index_of_index.txt")
    
    # with open("index.txt", 'r', encoding="utf-8") as file:
    #     for key in index_dictionary:
    #         file.seek(index_dictionary[key], 0)
    #         print(file.readline())
    
    
