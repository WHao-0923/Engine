from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import os, json, pickle
from collections import defaultdict
from invert_index import InvertedIndex
import requests
import time

word_freq = defaultdict(int)
ID_dict = defaultdict(str)
ID_count = 1
TEST_SIZE = 10

index_dict = InvertedIndex()


def createID(url):
    global ID_count
    if url not in ID_dict.values():
        ID_dict[ID_count] = url
        ID_count += 1
        return ID_count - 1
    else:
        return list(ID_dict.keys())[list(ID_dict.values()).index(url)]


def read_files():
    #path_to_json = 'DEV/www_ics_uci_edu/'
    path_to_json = 'DEV/'
    # Get all the directories within the path
    dirs = [path for path in os.listdir(path_to_json)]
    json_files = []
    for d in dirs:
        path = path_to_json + d + '/'
        print(path)
        # Process files from each directory
        dir_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        process_files(path,dir_files)
    
def process_files(json_path,files):
    counter = 1
    print(f"STARTING: {json_path}, TEST SIZE: {str(TEST_SIZE)}" )
    for file_name in files:
        # politeness 0.3s:
        time.sleep(0.3)
        if counter > TEST_SIZE:
            break
        # Keep track of progress
        if counter % (TEST_SIZE//10) == 0:
            print("INDEXING...: " + str(counter))
        counter += 1
        with open(os.path.join(json_path, file_name), 'r') as f:
            # loads the dictionary inside each json file
            data = json.load(f)
            # Get three elements
            url = data['url']
            content = data['content']
            encode = data['encoding']

            # Defragment the url
            if "#" in url:
                url = url.split('#')[0]
            # Use request to check url's status code
            try:
                response = requests.head(url, allow_redirects=False, timeout=5)
                if response.status_code != 200 :
                    # check if redirects
                    if response.status_code in (301, 302, 303, 307, 308):
                        redirect_response = requests.head(response.url, allow_redirects=False,timeout=5)
                        # check the status code for redirected url
                        if redirect_response.status_code != 200:
                            continue
                        else:
                            url = redirect_response.url
                    else:
                        continue
            except requests.exceptions.Timeout:
                # Request timeout
                print("The request timed out")
                continue
            except requests.exceptions.RequestException:
                # error in sending the request
                print("Request ERROR")
                continue
            
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
            if doc_ID in index_dict.index[word]:
                index_dict.index[word][doc_ID] += 1
            else:
                index_dict.index[word][doc_ID] = 1
    return list(set(tokens))

# start the program
read_files()

with open('index.pkl', 'wb') as f:
    pickle.dump(index_dict.index, f)

# get size of the file in KB
file_size = os.path.getsize('index.pkl') / 1024

# generate report
with open('report.txt', 'w+') as file:
    file.write("Number of Documents: " + str(ID_count))
    file.write("\n\n")
    file.write("Number of Unique Tokens: " + str(len(index_dict.index)))
    file.write("\n\n")
    file.write("File size of index in disk is " + str(round(file_size,2)) + "KB")

# for k,v in index_dict.index.items():
#     print(f"###########{k}: -------------{v}")
#     print(f'url {ID_dict[list(v.keys())[0]]} for key {v}')

