import generate_index
import math
import heapq


index_dict_1 = {"hello" : {12: [3, 10], 11: [4, 0], 1: [4, 0]}, "world" : {12: [3, 0], 11: [3, 0]}} #index_dict
total_count_1 = 50000 #number of document

# computer tf-idf for a index_dict
def compute_tfidf(index_dict, total_count):
    tfidf_dict = {}
    for token, doc_freq in index_dict.items():
        for doc_id, freq in doc_freq.items():
            df = len(doc_freq)
            tf = freq[0]
            weight = freq[1]
            tf_idf = (1 + math.log(tf, 2) * weight) * math.log(total_count/df, 2)
            if doc_id in tfidf_dict:
                tfidf_dict[doc_id] += tf_idf
            else:
                tfidf_dict[doc_id] = tf_idf
    #tfidf_dict = dict(sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True))
    #print(tfidf_dict)

    # use heap directly
    return dict(heapq.nlargest(1000,tfidf_dict.items(),key=lambda item: item[1])) #{11: 35.180410274716046, 9: 13.609640474436812, 38: 13.609640474436812, 42: 13.609640474436812}

if __name__ == '__main__':
    compute_tfidf(index_dict_1, total_count_1)

# computer science
# hello world
# what is master of computer engineering
# study of machienaiofhdsao