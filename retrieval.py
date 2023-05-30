import json
import time
import ast
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
import ranking

with open("perform_index.json",'r') as f:
    perform_index = json.load(f)
#print(perform_index)
query = ''
print("   ########## ##########")
print("WELCOME TO OUR SEARCH ENGINE")
while True:
    query = input("> ").lower()

    stemmer = SnowballStemmer('english', ignore_stopwords=True)

    start_time = time.time()
    if query == '!quit':
        break
    # sort words for query
    words = sorted(query.split())
    # [people,running]
    # [people,run] [people,running]
    #print("Here")

    # to search for base form only
    words = [stemmer.stem(w) for w in words]
    #print(words)
    byte_pos = dict()
    #print(perform_index)
    with open('main_index.txt', 'r+') as f:
        text = f.readline()
        
        pointer = 0
        last = text.split()[1]
        while text != '' and (pointer < len(words)):
            token = text.split()[0]
            # Compare with the cache dict for faster performance
            if words[pointer] in perform_index:
                byte_pos[words[pointer]] = str(perform_index[words[pointer]])
                pointer += 1
                continue
            # Comparison between tokens, save the byte position
            if token == words[pointer]:
                byte_pos[words[pointer]] = text.split()[1]
                pointer += 1
                continue
            elif token > words[pointer]:
                byte_pos[words[pointer]] = last
                pointer += 1
                continue
            last = text.split()[1]
            text = f.readline()
        # If not found, all append last position
        while pointer < len(words):
            byte_pos[words[pointer]] = last
            pointer += 1


    # List of docID sets
    ID_sets = set()
    # print(byte_pos)
    f2 = open('index.txt')
    final_docID_list = {}
    for k, v in byte_pos.items():
        # seek directly to the range of the index file
        f2.seek(int(v))
        token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        # print(token_tuple)
        while len(token_tuple) != 0 and token_tuple[0] < k:
            # print(token_tuple[0],k)
            # print("1")
            token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        if token_tuple[0] == k:
            #print(eval(token_tuple[1]).keys())
            #final_docID_list.append(set(eval(token_tuple[1]).keys()))
            final_docID_list[token_tuple[0]] = eval(token_tuple[1])
    # Initialize an empty dictionary
    result = {}

    # # Loop over the data
    # for key, value in final_docID_list.items():
    #     # Use ast.literal_eval to safely convert the string to a dictionary and assign it to the key in the result
    #     result[key] = ast.literal_eval(value)

    final = ranking.compute_tfidf(final_docID_list, 50000)
    #final = set.intersection(*final_docID_list)
    f2.close()

    if len(final) != 0:
        print(f"{len(final)} Results in ", end="")
        print("%s ms:" % round((time.time() - start_time) * 1000, 2))
        # generate URLs
        f = open('urls.json')
        ID_dict = json.load(f)
        rank = 1
        for i in final:
            print(f'{rank}: {ID_dict[str(i[0])]}')
            rank += 1
            if rank > 10:
                break
        f.close()
    else:
        print('No Result')
        print("--- %s ms ---" % round((time.time() - start_time) * 1000, 2))