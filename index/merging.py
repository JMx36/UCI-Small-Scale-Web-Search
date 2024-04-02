from utils.disk_operations import load_to_disk, get_from_disk
from utils import get_logger
from index.posting import Posting
import os
import re


# logger = get_logger("MERGING")

def merge_lists(list_A, list_B):
    merged_list = ""
    A_length = len(list_A)
    B_length = len(list_B)
    A_index = 0
    B_index = 0

    while A_index < A_length or B_index < B_length:
        # we get the doc id of the posting
        itemA = get_posting_id(list_A[A_index]) if A_index < A_length else None
        itemB = get_posting_id(list_B[B_index]) if B_index < B_length else None
        # condition if itemA is less than itemB
        if (not itemB and itemA) or (itemA and itemA < itemB):
            merged_list += f"({list_A[A_index]})"
            A_index += 1
        # condition if itemA is greater than itemB
        elif (not itemA and itemB) or (itemB and itemB < itemA):
            merged_list += f"({list_B[B_index]})"
            B_index += 1
        # condition if itemA is the same as itemB
        elif (itemA and itemB) and itemA == itemB:
            merged_list += f"({list_B[B_index]})"
            B_index += 1
            A_index += 1
        
        # Checking if this is the last element in the list   
        if A_index + 1 <= A_length or B_index + 1 <= B_length:
            merged_list += ", "
            
    return merged_list

def merge_indexes(first_index_path, second_index_path, new_file_path=""):
    # we get generators for both indexes
    first_generator = get_from_disk(first_index_path)
    second_generator = get_from_disk(second_index_path)

    first_done = False
    second_done = False
    line_A = None
    line_B = None
    # if there is not a file path given, then we use the first_index_path as the file path
    if not new_file_path:
        new_file_path = first_index_path
    
    # Open with writing mode
    with open(new_file_path, 'w') as file:
        similar_count = 0
        different_count = 0
        while  not first_done or not second_done:
            if not line_A and not first_done:
                try:
                    # move to the next line
                    line_A = next(first_generator)
                except StopIteration:
                    # StopIteration means we are done with the file
                    first_done = True
                    line_A = None
            if not line_B and not second_done:
                try: 
                    # move to the next line
                    line_B = next(second_generator)
                except StopIteration:
                    # StopIteration means we are done with the file
                    second_done = True
                    line_B = None
            
            # No lines to check, means we stop
            if not line_A and not line_B:
                break
            
            line_A, line_B, line_to_write = converge_indexes(line_A, line_B)
            
            # Update counts accordingly
            if (line_A and not line_B) or (line_B and not line_A):
                different_count += 1 
                
            if not line_B and not line_A:
                similar_count += 1
                
            file.write(line_to_write + "\n")
        # logger.info(f"Files: \n{first_index_path} \n {second_index_path}")
        # logger.info(f"SIMILAR: {similar_count}")
        # logger.info(f"Different: {different_count}")
        
def converge_indexes(line_A, line_B):
    tokenA, tokenB = None, None
    if line_A:
        line_A = line_A.strip("\n")
        # we parse the line of text into the token and postings
        tokenA, non_parsed_postingA = split_token(line_A)

    if line_B:
        line_B = line_B.strip("\n")
        # we parse the line of text into the token and postings
        tokenB, non_parsed_postingB = split_token(line_B)

    if (not tokenB and tokenA) or (tokenA and tokenA < tokenB):
        # return statement to know which line got used 
        # we need to know this because of the generators we are using
        return None, line_B, line_A
    elif (not tokenA and tokenB) or (tokenB and tokenB < tokenA):
        # return statement to know which line got used 
        # we need to know this because of the generators we are using
        return line_A, None, line_B
    elif (tokenA and tokenB) and tokenA == tokenB:
        # tokens are the same, so we merge the lists
        return None, None, f"{tokenA}: " + merge_lists(parsed_posting(non_parsed_postingA), parsed_posting(non_parsed_postingB))
        
def split_token(line: str):
    token_split = line.split(': ')
    return (token_split[0], token_split[1])

def parsed_posting(line: str):
    posting = re.findall(r'\((.*?)\)', line) 
    return posting

def get_posting_id(line: str):
    return int(line.split(', ')[0])
  
def parse_posting_values(line: str):
    return line.split(', ')
    
def sort_index(index):
    for token, posting_list in index.items():
        index[token] = sorted(posting_list, key=lambda a: a.get_id())

    return index

def get_equal_postings_id_set(postings_A : str, postings_B : str):
    # we assume postings_A is smaller than postings B
    equal_postings = []
    A_length = len(postings_A)
    B_length = len(postings_B)
    indexA = 0
    indexB = 0
    # parses the posting values of the first posting
    valuesA = parse_posting_values(postings_A[indexA])
    doc_idA = int(valuesA[0]) # gets doc id
    # parses the posting values of the second posting
    valuesB = parse_posting_values(postings_B[indexB])
    doc_idB = int(valuesB[0]) # gets doc id
    
    # loops until we don't have any postings to left over
    while indexA < A_length and indexB < B_length:
        # if it is equal we advance the postings
        if doc_idA == doc_idB:
            equal_postings.append(str(doc_idA) + ", ")
            indexA += 1
            indexB += 1
            if indexA >= A_length or indexB >= B_length:
                # print("BREAKING", indexA, indexB)
                break
            valuesA = parse_posting_values(postings_A[indexA])
            doc_idA = int(valuesA[0])
            valuesB = parse_posting_values(postings_B[indexB])
            doc_idB = int(valuesB[0])
        
        elif doc_idB >= doc_idA:
            # print("GREATER THAN", doc_idB, doc_idA)
            indexA += 1
            if indexA >= A_length:
                # print(">= BREAKING", indexA, indexB)
                break
            valuesA = parse_posting_values(postings_A[indexA])
            doc_idA = int(valuesA[0])
        
        elif doc_idB < doc_idA:
            indexB += 1
            if indexB >= B_length:
                continue
            valuesB = parse_posting_values(postings_B[indexB])
            doc_idB = int(valuesB[0])
    
    return equal_postings        


if __name__ == '__main__':
    # postings = '(1, 2), (3, 4)\n'
    # posting = re.findall(r'\((.*?)\)', postings) 
    # print(posting)
    
    # print(get_posting_id(posting[0]))
    
    tokenA = "1: (213, 2), (714, 6)"
    tokenB = "1: (6, 2), (7, 5)"
    print(converge_indexes(tokenA, tokenB))
    
    # file_path1 = "Merges/merge1.txt"
    # file_path2 = "Merges/merge2.txt"
    # merge_indexes(file_path1, file_path2, "Merges/merge3.txt")
    
    