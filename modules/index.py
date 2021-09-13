# Inverted Index implementation for blog document searching

from pathlib import Path
from typing import Iterable, List
# add the root directory for nltk_data folder
from nltk import data
data.path.append(str(Path(__file__).resolve().parents[1] / "nltk_data"))
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json
import re
import boto3
import os

class Document:
    """Represents a document that will be indexed. Args represent document fields (e.g., author).
    """
    
    def __init__(self, Id: int, *args):
        """Represents a document that will be indexed. Args represent document fields (e.g., author).

        Parameters
        ----------
        Id : int
            document Id used for indexing.
        """
        self.Id = Id
        self.fields = args

    def getTokens(self, parser: 'Parser') -> set:
        """Given a Parser object, this will return the set of tokens contained in the document.

        Parameters
        ----------
        parser : Parser

        Returns
        -------
        set
            The set of tokens in the document.
        Example
        -------
        >>> doc = Document("Joseph", "Blog Title", "This is the content in the blog that will be indexed.")
        >>> p = Parser()
        >>> tokens = doc.getTokens(p)
        >>> print(tokens)
        {'content', 'index', 'blog', 'titl'}
        """
        tokens = set()
        for field in self.fields:
            tokens = tokens.union(parser.parse(field))
        return tokens
        

class Parser:
    """Parsing object used to parse documents. 
    """
    # regex expression to remove html tags.
    # see https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string for details.
    HTML_CLEANER = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    
    def __init__(self, language='english'):
        """Parsing object used to parse documents. 

        Parameters
        ----------
        language : str, optional
            language to use for stopwords, by default 'english'
        """
        self.language = language
        self.STOP_WORDS = set(stopwords.words(language))
        self.ps = PorterStemmer()
        
    def _charFilter(self, document_field: str) -> str:
        """lowercases string and removes html tags.

        Returns
        -------
        str
            filtered and lowered string.
        """
        content_str = document_field.lower()
        content_cleaned = re.sub(self.HTML_CLEANER, '', content_str)
        return content_cleaned
    
    def _tokenFilter(self, tokens: Iterable) -> list:
        """Filters out stopwords from a iterable of tokens.

        Parameters
        ----------
        tokens : Iterable

        Returns
        -------
        list
            List of tokens after filtering.
        """
        tokens = [
            token for token in tokens 
            if token.isalpha() and not token in self.STOP_WORDS
        ]
        return tokens

    def _stemTokens(self, tokens: Iterable) -> list:
        """stems tokens (e.g., 'title' -> 'titl')
        """
        return [self.ps.stem(token) for token in tokens]
    
    def parse(self, document_field: str) -> set:
        """parses a document field into tokens to be indexed.

        Parameters
        ----------
        document_field : str

        Returns
        -------
        set
            Set of Tokens to be indexed.
        """
        filtered = self._charFilter(document_field)
        tokens = word_tokenize(filtered)
        tokens = self._tokenFilter(tokens)
        tokens = self._stemTokens(tokens)
        return set(tokens)
        
        
class InvertedIndex:
    """In-memory Inverted Index object.
    """
    
    def __init__(self, from_file=True, in_s3=False, file_path="index.json"):
        """In-memory Inverted Index object.

        Parameters
        ----------
        from_file : bool, optional
            If True, initializes the index from a file, by default True
        in_s3 : bool, optional
            If True, reads the file from S3 bucket, by default False
        """
        self.from_file = from_file
        self.file_path = Path(file_path)
        self.in_s3 = in_s3
        self.bucket = 'joseph-blog-media'
        self.parser = Parser()
        if from_file and in_s3:
            self.client = boto3.client('s3', 
                aws_access_key_id=os.environ.get('AWS_S3_ACCESS_KEY'), 
                aws_secret_access_key=os.environ.get('AWS_S3_SECRET_KEY')
                )
            result = self.client.get_object(Bucket=self.bucket, Key="index.json")
            self.index = json.loads(result["Body"].read().decode('utf-8'))
        elif from_file:
            index_file = Path(file_path)
            if index_file.is_file():
                mode = "r"
            # see https://docs.python.org/3/library/functions.html#open for more details
            else:
                mode = "w+"
            with open(index_file, mode) as f:
                self.index = json.load(f)
        else:
            self.index = dict()
    
    def add(self, document: Document) -> None:
        """Adds a document to the index.

        Parameters
        ----------
        document : Document
        """
        tokens = document.getTokens(self.parser)
        for token in tokens:
            if token not in self.index:
                self.index[token] = [document.Id]
            else:
                docs = self.index[token]
                if document.Id not in docs:
                    self.index[token].append(document.Id)

    def remove(self, document: Document) -> None:
        """Removes a document from the index.

        Parameters
        ----------
        document : Document
        """
        for token, doc_entries in self.index.items():
            if document.Id in doc_entries:
                doc_entries.remove(document.Id)
                # the token has no entries
                if not doc_entries:
                    del self.index[token]
                
    def save(self) -> None:
        """Saves the index back to disk.
        """
        if self.from_file and self.in_s3:
            #self.client.delete_object(Bucket=self.bucket, Key='index.json')
            self.client.put_object(Body=json.dumps(self.index, indent=4), Bucket=self.bucket, Key="index.json")
        else:
            with open(self.file_path, "w") as f:
                json.dump(self.index, f, indent=4)

    def search(self, search) -> set:
        """Searches the index, returning document Ids that contain the phrase/word.

        Parameters
        ----------
        search : str

        Returns
        -------
        set
            The set of document IDs containing all the searched terms.
        """
        search_tokens = self.parser.parse(search)
        results = []
        for token in search_tokens:
            if token in self.index:
                results.append(set(self.index[token]))
        if results:
            return set.intersection(*results)
        else:
            return set()

    def cleanup(self):
        """Cleans up the inverted index, deleting tokens that don't have an doc entries.
        """
        tokens_to_remove = []
        for token in self.index:
            # list is empty
            if not self.index[token]:
                tokens_to_remove.append(token)
        for token in tokens_to_remove:
            del self.index[token]
        self.save()
