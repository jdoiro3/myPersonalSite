from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json
import re
from pathlib import Path

class Document:
    
    def __init__(self, Id, *args):
        self.Id = Id
        self.fields = args

    def getTokens(self, parser):
        tokens = set()
        for field in self.fields:
            tokens = tokens.union(parser.parse(field))
        return tokens
        

class Parser:
    
    HTML_CLEANER = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    
    def __init__(self, language='english'):
        self.language = language
        self.STOP_WORDS = set(stopwords.words(language))
        self.ps = PorterStemmer()
        
    def _charFilter(self, content_str):
        content_str = content_str.lower()
        content_cleaned = re.sub(self.HTML_CLEANER, '', content_str)
        return content_cleaned
    
    def _tokenFilter(self, tokens):
        tokens = [
            token for token in tokens 
            if token.isalpha() and not token in self.STOP_WORDS
        ]
        return tokens

    def _stemTokens(self, tokens):
        return [self.ps.stem(token) for token in tokens]
    
    def parse(self, content_str):
        filtered = self._charFilter(content_str)
        tokens = word_tokenize(filtered)
        tokens = self._tokenFilter(tokens)
        tokens = self._stemTokens(tokens)
        return set(tokens)
        
        
class InvertedIndex:
    
    def __init__(self, from_file=True):
        self.parser = Parser()
        self.index_json = Path("index.json")
        if from_file:
            if self.index_json.is_file():
                with open(self.index_json, "r") as f:
                    self.index = json.load(f)
            else:
                self.index = dict()
    
    def add(self, document):
        tokens = document.getTokens(self.parser)
        for token in tokens:
            if token not in self.index:
                self.index[token] = [document.Id]
            else:
                docs = self.index[token]
                if document.Id not in docs:
                    self.index[token].append(document.Id)

    def remove(self, document):
        for doc_entries in self.index.values():
            if document.Id in doc_entries:
                doc_entries.remove(document.Id)
                
    def save(self):
        with open(self.index_json, "w") as f:
            json.dump(self.index, f, indent=4)

    def search(self, search):
        search_tokens = self.parser.parse(search)
        results = []
        for token in search_tokens:
            if token in self.index:
                results.append(set(self.index[token]))
        if results:
            return set.intersection(*results)
        else:
            return set()