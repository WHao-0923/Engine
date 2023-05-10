# Requiredment for MS1

import re
from collections import defaultdict
from bs4 import BeautifulSoup


class InvertedIndex:
    def __init__(self):
        # initialize a general dictionary
        self.index = defaultdict(list)

    def add_document(self, doc_id, tokens):
        # Get the pure
        for token in tokens:
            self.index[token].append(doc_id)

    def get_documents(self, word):
        return self.index.get(word.lower(), [])