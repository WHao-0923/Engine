# Team Members:
# Joanna Chen, 66238804
# Yui Guo, 75458764
# Weiyu Hao, 59955246
# Ruiyang Wang, 52294785

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import os, json, pickle
from collections import defaultdict
from invert_index import InvertedIndex
from nltk.stem import PorterStemmer

# import requests
import time

word_freq = defaultdict(int)
ID_dict = defaultdict(str)  # {doc_id: url}
ID_count = 1
TEST_SIZE = 999999

batch_size = 20000  # 20000
file_index = 1

file_list = []

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
        # Process files from each directory
        dir_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        process_files(path, dir_files)


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
            text = soup.get_text()

            tokens = tokenize(text, doc_ID)

    # for last time append
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


def merge_file():
    file1 = open(file_list[0], "r+")
    file2 = open(file_list[1], "r+")
    file3 = open(file_list[2], "r+")
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
                merge_dict = {k: sum(d[k] for d in merge_list if k in d) for k in set(k for d in merge_list for k in d)}
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

    sorted_index = sorted(index_dict.index.items())

    count = 0

    merge_file()

    f2 = open('main_index.txt', "w+")

    # with open('ori_index.txt', 'w') as f:
    #     # f2.write(str(len(sorted_index)//100) + '\n')
    #     for i in sorted_index:
    #         if count % 1000 == 0:
    f = open('index.txt', "r")
    byte = 0
    text = f.readlines()
    for i in text:
        #f2.write(f"{i[0]} {os.stat('ori_index.txt').st_size}\n")
        f2.write(f"{i.split('---')[0]} {byte}\n")
        byte += len(i.encode())
            #f.write(f'{i[0]}---{i[1]}\n')
            #f.flush()
            #count += 1
    f2.close()
    f.seek(7801)
    print(f.readline())
    f.close()

    with open('urls.json', 'w') as f3:
        json.dump(ID_dict, f3)

    # get size of the file in KB
    file_size = os.path.getsize('index.txt') / 1024

    # generate report
    with open('report.txt', 'w+') as file:
        file.write("Team Members:\n")
        file.write("Joanna Chen, 66238804\n")
        file.write("Yui Guo, 75458764\n")
        file.write("Weiyu Hao, 59955246\n")
        file.write("Ruiyang Wang, 52294785\n")
        file.write("\n\n\n\n")
        file.write("Number of Documents: " + str(ID_count))
        file.write("\n\n")
        file.write("Number of Unique Tokens: " + str(len(index_dict.index)))
        file.write("\n\n")
        file.write("File size of index in disk is " + str(round(file_size, 2)) + "KB")
        file.write("\n\n")
        file.write("DocID with URLs:\n")
        for k, v in ID_dict.items():
            file.write(f'DocID {k} ----- {v}\n')

    # for k,v in index_dict.index.items():
    #     print(f"###########{k}: -------------{v}")
    #     print(f'url {ID_dict[list(v.keys())[0]]} for key {v}')