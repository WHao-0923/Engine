# Requiredment for MS1

import re
from collections import defaultdict
from bs4 import BeautifulSoup


class InvertedIndex:
    def __init__(self):
        # initialize a general dictionary
        self.index =  defaultdict(dict)

    def get_documents(self, word):
        return self.index.get(word.lower(), [])