# Team Members:
# Joanna Chen, 66238804
# Yui Guo, 75458764
# Weiyu Hao, 59955246
# Ruiyang Wang, 52294785

from bs4 import BeautifulSoup, SoupStrainer
import nltk
from nltk.tokenize import word_tokenize
import os, json, pickle
from collections import defaultdict
from invert_index import InvertedIndex
from nltk.stem import PorterStemmer
from nltk.corpus import words
from lxml import etree

# import requests
import time

#nltk.download('words')
english_words = words.words()
perform_index = {}

#word_freq = defaultdict(int)
ID_dict = defaultdict(str)  # {doc_id: url}
ID_count = 1
TEST_SIZE = 999999

batch_size = 20000  # 20000
file_index = 1

file_list = []

index_dict = InvertedIndex()

ps = PorterStemmer()

def createID(url):
    global ID_count
    if url not in ID_dict.values():
        ID_dict[ID_count] = url
        ID_count += 1
        return ID_count - 1
    else:
        return list(ID_dict.keys())[list(ID_dict.values()).index(url)]


def read_files():
    # path_to_json = 'DEV/www_ics_uci_edu/'
    path_to_json = 'DEV/'
    # Get all the directories within the path
    dirs = [path for path in os.listdir(path_to_json)]
    json_files = []
    for d in dirs:
        if d.startswith('.'):
            continue
        path = path_to_json + d + '/'
        print(path)

        # testing only
        #if path == 'DEV/cbcl_ics_uci_edu/':

        # Process files from each directory
        dir_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
    
        process_files(path, dir_files)
    # for last time append
    global file_index
    print(f'####################\n{ID_count}\n######################')
    memory_file = "memory_file_" + str(file_index) + ".txt"
    file_list.append(memory_file)
    f = open(memory_file, "w")
    small_sorted_dict = sorted(index_dict.index.items())
    for i in small_sorted_dict:
        f.write(f'{i[0]}---{i[1]}\n')
    file_index += 1
    print(file_index)
    index_dict.index = defaultdict(dict)
    f.close()


def process_files(json_path, files):
    counter = 1

    print(f"STARTING: {json_path}, TEST SIZE: {str(TEST_SIZE)}")
    counter = 1
    for file_name in files:
        # # politeness 0.3s:
        # time.sleep(0.3)
        if counter > TEST_SIZE:
            break

        # Keep track of progress
        if counter % 50 == 0:
            print("INDEXING...: " + str(counter))
        counter += 1

        global file_index
        if ID_count % batch_size == 0:
            print(f'####################\n{ID_count}\n######################')
            memory_file = "memory_file_" + str(file_index) + ".txt"
            file_list.append(memory_file)
            f = open(memory_file, "w")
            small_sorted_dict = sorted(index_dict.index.items())
            for i in small_sorted_dict:
                f.write(f'{i[0]}---{i[1]}\n')
            file_index += 1
            print(file_index)
            index_dict.index = defaultdict(dict)
            f.close()

        with open(os.path.join(json_path, file_name), 'r') as f:
            # loads the dictionary inside each json file
            data = json.load(f)
            # Get three elements
            url = data['url']
            content = data['content']
            encode = data['encoding']

            # no need to check validility of url
            # check if url is duplicated
            doc_ID = createID(url)
            # print(f'doc_ID: {doc_ID}')

            soup = BeautifulSoup(content, "html.parser")
            h1 = soup.find('h1')
            h2 = soup.find('h2')
            h3 = soup.find('h3')
            b = soup.find('b')
            text = soup.get_text()

            tokens = tokenize(text, doc_ID, h1,h2,h3,b)

    #print(word_freq)

    
def score_token(text, token,h1,h2,h3,b):
    # Define a dictionary to hold the scores
    tag_scores = {'h1': 20, 'h2': 19, 'h3': 18, 'b': 10}

    # # Define a CSS selector to find multiple tags
    # selector = 'h1, h2'

    # # Find all occurrences of the specified tags using the CSS selector
    # tags = soup.select(selector)

    #soup = BeautifulSoup(text, 'html.parser')

    if h1:
        if token in h1.get_text():
            #print('h1')
            return [token, 20]
    if h2:
        if token in h2.get_text():
            #print('h2')
            return [token, 19]
    if h3:
        if token in h3.get_text():
            #print('h3')
            return [token, 18]
    if b:
        if token in b.get_text():
            #print('b')
            return [token, 10]

    # # Find the first tag of this type
    # for tag in tags:
    #     #print(tag)
    #     if token in tag.get_text():
    # #return [token, 0]
    #         return [token, tag_scores.get(tag.name, 0)]
    
    # If the token was not found in any of the tags, return a score of 0
    return [token, 0]

def tokenize(text, doc_ID, h1,h2,h3,b):
    # nltk to tokenize the text provided
    tokens = word_tokenize(text)

    # update the word_frequency dictionary and give the word count of this page
    token_count = 0
    for token in tokens:
        word = token.lower()
        if word.isalnum():
            #find the score of this token for the first time it appears in the context['This', 19]
            word2 = ps.stem(word)
            
            #word_freq[word2] += 1
            if doc_ID in index_dict.index[word2]:
                #just increment the frequency within a doc
                index_dict.index[word2][doc_ID][0] += 1
            else:
                #update the token_value according to the first appearance
                token_value = score_token(text, word,h1,h2,h3,b)[1]
                token_count += 1
                index_dict.index[word2][doc_ID] = [1, token_value] # [1, token_value]
    #print(index_dict.index)
    return list(set(tokens))


def merge_file():
    
    # file1 = open(file_list[0], "r+")
    # file2 = open(file_list[1], "r+")
    # file3 = open(file_list[2], "r+")

    file1 = open('memory_file_1.txt', "r+")
    file2 = open('memory_file_2.txt', "r+")
    file3 = open('memory_file_3.txt', "r+")

    t1 = file1.readline()
    t2 = file2.readline()
    t3 = file3.readline()

    counter = 0
    while t1 != '' or t2 != '' or t3 != '':
        if counter % 100 == 0:
            #print(t1,t2,t3)
            pass
        counter += 1
        token_list = [None, None, None] #['token', {}]
        if t1 != '':
            token1 = t1.split("---")
            token_list[0] = token1
        if t2 != '':
            #print("2: ",t2)
            token2 = t2.split("---")
            token_list[1] = token2
        if t3 != '':
            token3 = t3.split("---")
            token_list[2] = token3

        # Find the smallest token from lists and the index
        filtered_list = [word for word in token_list if word is not None]
        min_list = min(filtered_list,key=lambda x:x[0]) #['token', {}]
        min_token = min_list[0] #return token
        min_file = token_list.index(min_list) #return file number

        next_list = [min_file] #files that need to move to next line
        merge_list = []
        min_dict = eval(token_list[min_file][1])
        merge_list.append(min_dict)

        #merged_file = open('index.txt', 'a')
        with open('index.txt', 'a') as merged_file:

            for i in range(len(token_list)):
                if i != min_file:
                    if token_list[i] != None and min_token == token_list[i][0]:
                        merge_list.append(eval(token_list[i][1]))
                        next_list.append(i)

            if len(merge_list) > 1:
                merge_dict = merge_list[0]
                for i in merge_list[1:]:
                    for k, v in i.items():
                        merge_dict[k] = v
                #print(merge_dict)
                #print(min_token + '---' + str(merge_dict))
                merged_file.write(min_token + '---' + str(merge_dict) + '\n')
                merged_file.flush()
            else:
                #print(min_token + '---' + str(merge_dict))
                merged_file.write(min_token + '---' + str(min_dict) + '\n')
                merged_file.flush()

            if len(next_list) == 0:
                return

            for i in next_list: # [0,1]
                #print(f"printing next list: {i}")
                if i == 0 and t1 != '':
                    t1 = file1.readline()
                   #print(f"1!!!{t1}")
                elif i == 1 and t2 != '':
                    t2 = file2.readline()
                    #print(f"2!!!{t2}")
                elif i == 2 and t3 != '':
                    t3 = file3.readline()
                #print(f"3!!!{t3}")
        #merged_file.close()




# start the program
if __name__ == '__main__':
    read_files()

    # sorted_index = sorted(index_dict.index.items())

    count = 0

    merge_file()

    perform_index = {}

    f2 = open('main_index.txt', "w+")

    # with open('ori_index.txt', 'w') as f:
    #     # f2.write(str(len(sorted_index)//100) + '\n')
    #     for i in sorted_index:
    #         if count % 1000 == 0:
    f = open('index.txt', "r")
    byte = 0
    text = f.readlines()

    common_words = ('computer','science','machine','learning','engineering',"algorithm",\
                "data", "program", "code", "variable", "function", "class", "object", "interface", \
                "method", "loop", "conditional", "what", "array", "list", "string", "integer", "boolean",\
                 "file", "database", "network", "server", "client", "protocol", "encryption",\
                  "decryption", "memory", "cpu", \
                  "gpu", "cache", "thread", "process", "concurrency", "parallelism", "big data", \
                  "artificial intelligence", "machine learning", "deep learning", "neural network",\
                   "cloud computing", "virtualization", "or", "web development", "api", "framework", "security", "vulnerability", "debugging", "testing", "software", "hardware", "database", "management", "data", "structure", "algorithmic", "to", "complexity", "be", "recursion", "sorting", "searching", "graph", "tree", "linked", "list", "queue", "stack", "hashing", "operating", "system", "file", "networking", "client", "server", "internet", "cybersecurity", "cryptography", "authentication", "authorization", "privacy", "integrity", "cloud", "storage", "distributed", "computing", "virtual", "machine", "web", "not", "application", "mobile", "app", "responsive", "design", "user", "interface", "experience", "agile", "development", "version")

    for i in text:
        #f2.write(f"{i[0]} {os.stat('ori_index.txt').st_size}\n")
        # save the most common token in cache
        if i.split('---')[0] in common_words:
            perform_index[i.split('---')[0]] = eval(i.split('---')[1])

        if count % 800 == 0: # this creates 800 main index, and each with 800 interval
            f2.write(f"{i.split('---')[0]} {byte}\n")
    
        byte += len(i.encode())
            #f.write(f'{i[0]}---{i[1]}\n')
            #f.flush()
        count += 1
    f2.close()
    f.seek(7801)
    #print(f.readline())
    f.close()
    with open("perform_index.json",'w') as file:
        json.dump(perform_index,file)
    # with open('urls.json', 'w') as f3:
    #     json.dump(ID_dict, f3)

    # # get size of the file in KB
    # file_size = os.path.getsize('index.txt') / 1024

    # # generate report
    # with open('report.txt', 'w+') as file:
    #     file.write("Team Members:\n")
    #     file.write("Joanna Chen, 66238804\n")
    #     file.write("Yui Guo, 75458764\n")
    #     file.write("Weiyu Hao, 59955246\n")
    #     file.write("Ruiyang Wang, 52294785\n")
    #     file.write("\n\n\n\n")
    #     file.write("Number of Documents: " + str(ID_count))
    #     file.write("\n\n")
    #     file.write("Number of Unique Tokens: " + str(len(index_dict.index)))
    #     file.write("\n\n")
    #     file.write("File size of index in disk is " + str(round(file_size, 2)) + "KB")
    #     file.write("\n\n")
    #     file.write("DocID with URLs:\n")
    #     for k, v in ID_dict.items():
    #         file.write(f'DocID {k} ----- {v}\n')

    # for k,v in index_dict.index.items():
    #     print(f"###########{k}: -------------{v}")
    #     print(f'url {ID_dict[list(v.keys())[0]]} for key {v}')
