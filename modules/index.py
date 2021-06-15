from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import re
from nltk.corpus import wordnet

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemma_names():
            synonyms.add(lemma)
    return synonyms

class Document:
    
    def __init__(self, Id, content):
        self.Id = Id
        self.content = content
        

class Parser:
    
    HTML_CLEANER = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    
    def __init__(self, language='english'):
        self.language = language
        self.STOP_WORDS = set(stopwords.words(language))
        
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
    
    def parse(self, content_str):
        filtered = self._charFilter(content_str)
        tokens = word_tokenize(filtered)
        tokens_filtered = self._tokenFilter(tokens)
        return set(tokens_filtered)
        
        
class InvertedIndex:
    
    def __init__(self):
        self.parser = Parser()
        self.index = dict()
    
    def add(self, document):
        tokens = self.parser.parse(document.content)
        for token in tokens:
            if token not in self.index:
                self.index[token] = [document.Id]
            else:
                docs = self.index[token]
                if document.Id not in docs:
                    self.index[token].append(document.Id)
                
    def save(self):
        with open("index.json", "w") as f:
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