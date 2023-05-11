from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import os, json
from collections import defaultdict
from invert_index import InvertedIndex

word_freq = defaultdict(int)
ID_dict = defaultdict(str)
ID_count = 1

index_dict = InvertedIndex()


def createID(url):
    global ID_count
    if url not in ID_dict.values():
        ID_dict[ID_count] = url
        ID_count += 1
        return ID_count - 1
    else:
        return ID_dict.keys()[ID_dict.values().index(url)]


def read_files():
    path_to_json = 'DEV/www_ics_uci_edu/'
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    counter = 0
    for file_name in json_files:
        print(counter)
        if counter > 100:
            break
        counter += 1
        with open(os.path.join(path_to_json, file_name), 'r') as f:
            # loads the dictionary inside each json file
            data = json.load(f)
            # Get three elements
            url = data['url']
            content = data['content']
            encode = data['encoding']

            # check if url is duplicated
            doc_ID = createID(url)
            #print(f'doc_ID: {doc_ID}')

            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()

            tokens = tokenize(text,doc_ID)

def tokenize(text, doc_ID):
    # nltk to tokenize the text provided
    tokens = word_tokenize(text)

    # update the word_frequency dictionary and give the word count of this page
    for token in tokens:
        word = token.lower()
        if word.isalnum():
            word_freq[word] += 1
            index_dict.index[word][doc_ID] += 1
    return list(set(tokens))


read_files()
'''
for k, v in ID_dict.items():
    print(f"###########{k}: -------------{v}")
'''

for k,v in index_dict.index.items():
    print(f"###########{k}: -------------{v}")
    print(f'url {ID_dict[list(v.keys())[0]]} for key {v}')

