import json
import time
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import ranking
from summarizer import Summarizer

with open("perform_index.json", 'r') as f:
    perform_index = json.load(f)

OPENAI_AIPI_KEY = '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'
openai_summarizer = Summarizer(OPENAI_AIPI_KEY)

stop_words = set(stopwords.words('english'))

def search(query: str):
    results = []
    speed = {}
    summary = {}

    stemmer = SnowballStemmer('english', ignore_stopwords=True)
    query = query.lower()
    start_time = time.time()

    sort_words = sorted(list(set(query.split())))

    stop_only = 0
    percent_count = 0
    words = []
    for token in sort_words:
        if token in stop_words:
            percent_count += 1
        else:
            words.append(token)

    if len(sort_words) > 0 and percent_count / len(sort_words) > 0.75:
        stop_only = 1
    if stop_only:
        words = sort_words
    words = [stemmer.stem(w) for w in words]

    byte_pos = dict()

    with open('main_index.txt', 'r+') as f:
        #main_index_time = time.time()
        text = f.readline()
        
        pointer = 0
        last = text.split()[1]
        while text != '' and (pointer < len(words)):
            token = text.split()[0]
            # # Compare with the cache dict for faster performance
            # if words[pointer] in perform_index:
            #     byte_pos[words[pointer]] = str(perform_index[words[pointer]])
            #     pointer += 1
            #     continue

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
    #print("--- main index %s ms ---" % round((time.time() - main_index_time) * 1000, 2))

    locate_index_time = time.time()
    # List of docID sets
    ID_sets = set()
    # print(byte_pos)
    f2 = open('index.txt')
    final_docID_list = {}
    for k, v in byte_pos.items():
        if k in perform_index:
            #print(k,perform_index[k])
            final_docID_list[k] = perform_index[k]
            continue
        # seek directly to the range of the index file
        f2.seek(int(v))
        token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        # print(token_tuple)
        #loop_index_time = time.time()
        while len(token_tuple) != 0 and token_tuple[0] < k:
            token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        #print("     --- loop index %s ms ---" % round((time.time() - loop_index_time) * 1000, 2))
        if token_tuple[0] == k:
            #print(eval(token_tuple[1]).keys())
            #final_docID_list.append(set(eval(token_tuple[1]).keys()))
            #append_index_time  = time.time()

            final_docID_list[token_tuple[0]] = eval(token_tuple[1])
            #print("     --- append index %s ms ---" % round((time.time() - append_index_time) * 1000, 2))
    print("--- locate index %s ms ---" % round((time.time() - locate_index_time) * 1000, 2))
    rank_index_time = time.time()

    final = ranking.compute_tfidf(final_docID_list, 50000)
    print("--- rank %s ms ---" % round((time.time() - rank_index_time) * 1000, 2))
    #final = set.intersection(*final_docID_list)
    f2.close()
    
    speed = {}
    speed['number'] = len(final)
    speed['query_time'] = 0
    speed['gpt_time'] = 0
    summary = {}
    summary['summary'] = ''
    pages = []
    if len(final) != 0:
        f = open('urls.json')
        ID_dict = json.load(f)
        rank = 1
        for i in final:
            result_dict = {}
            result_dict['rank'] = rank
            result_dict['url'] = ID_dict[str(i[0])]
            results.append(result_dict)
            rank += 1
            if rank > 10:
                break
        f.close()
        urls = []
        for result in results:
            urls.append(result['url'])
        speed['query_time'] = round((time.time() - start_time) * 1000, 2)
        summary_time = time.time()
        summary['summary'] = openai_summarizer.summarize(urls)
        speed['gpt_time'] = round((time.time() - summary_time) * 1000, 2)

        
    else:
        results.append({'rank': 'N/A', 'url': 'No results', 'summary': ''})
        speed['query_time'] = 0
        speed['gpt_time'] = 0
        summary['summary'] = ''

    return results, summary, speed
