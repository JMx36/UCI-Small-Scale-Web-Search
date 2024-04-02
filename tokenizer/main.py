import sys
import json
from tokenizer.tokenizer import gettokens, frequency


def main():
    # Check if a file path is provided as a command line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <jsonfilepath>")
        sys.exit(1)
    jsonfile_path = sys.argv[1]

    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)  # Load JSON file
            # Assume that the text content is under a key named 'content'. Adjust if necessary.
            text_content = json_data["content"]
            tokens = get_tokens(text_content)
            token_count_map = frequency(tokens)

            #iterates over each token and the count of it.
            for token, count in token_count_map.items():
                print(f"{token} -> {count}")


    #handle if Json file is not found
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        sys.exit(1)
    #Handle if not a valid JSON file
    except json.JSONDecodeError:
        print(f"Error: File is not a valid JSON file: {json_file_path}")
        sys.exit(1)
    # handle if the Json file does not include "content key"
    except KeyError:
        print(f"Error: JSON does not contain 'content' key")
        sys.exit(1)
    #Handle any other unexpected error
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name == "__main":
    main()
