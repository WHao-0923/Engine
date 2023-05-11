# Requiredment for MS1

import re
from collections import defaultdict
from bs4 import BeautifulSoup


class InvertedIndex:
    def __init__(self):
        # initialize a general dictionary
        self.index =  defaultdict(lambda : defaultdict(int))

    # def add_document(self, doc_id, tokens):
    #     # Get the pure
    #     for token in tokens:
    #         self.index[token][doc_id] += 1

    def get_documents(self, word):
        return self.index.get(word.lower(), [])