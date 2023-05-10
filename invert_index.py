# Requiredment for MS1

import re
from collections import defaultdict
from bs4 import BeautifulSoup


class InvertedIndex:
    def __init__(self):
        # initialize a general dictionary
        self.index = defaultdict(list)

    def 

    def add_document(self, doc_id, text):
        # Get the pure
        words = re.findall(r'' text.lower())
        for word in words:
            self.index[word].append(doc_id)

    def get_documents(self, word):
        return self.index.get(word.lower(), [])