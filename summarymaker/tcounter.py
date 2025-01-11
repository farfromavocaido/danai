# tcounters.py
# ---------------------------------------------------------
# For counting tokens, using tiktoken or any other method you wish.

import tiktoken

def tokencount_file(input_file, model="gpt-4o"):
    """
    Count the number of tokens in a text file using the specified model.
    """
    encoding = tiktoken.encoding_for_model(model)

    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    content = read_file(input_file)
    token_count = len(encoding.encode(content))
    return token_count


def tokencount_text(text, model="gpt-4o"):
    """
    Count the number of tokens in a string using the specified model.
    """
    encoding = tiktoken.encoding_for_model(model)
    token_count = len(encoding.encode(text))
    return token_count

