import nltk

word_freq = defaultdict(0)
doc_ID = defaultdict("")
ID_count = 1
def tokenize(text):
    stop_words = set(stopwords.words("english"))
    # nltk to tokenize the text provided
    tokens = word_tokenize(text)

    # update the word_frequency dictionary and give the word count of this page
    for token in tokens:
        word = token.lower()
        if word.isalnum() and word not in stop_words:
            word_freq[word] += 1

    return word_freq

def createID(url):
    if url not in doc_ID.values():
        doc_ID[ID_count] = url
        ID_count += 1
    return ID_count
