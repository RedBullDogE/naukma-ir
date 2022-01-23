import string
from multiprocessing.sharedctypes import Value
from pathlib import Path

from nltk.tokenize import word_tokenize

from helpers import CollectionException, get_collection_paths

DATA_DIR = Path("./data")


class TextCollection:
    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.title: str = path.name
        self.raw_text: str = ""
        self.tokens: list = []
        self.unique_tokens: set = set()

        self._read_file()

    def _read_file(self):
        """Read data from file and save it as string to internal variable"""

        with open(self.path, "r", encoding="utf-8") as f:
            self.raw_text = f.read()
            return self.raw_text

    def clean(self):
        """Remove punctuation symbols from tokens and make them lowercase"""

        if not self.tokens:
            raise CollectionException(
                "Token collection is empty. Please, run tokenize first"
            )

        self.tokens = [
            token.lower() for token in self.tokens if token not in string.punctuation
        ]
        return self.tokens

    def tokenize(self):
        self.tokens = word_tokenize(self.raw_text)
        return word_tokenize(self.raw_text)

    def get_unique(self):
        self.unique_tokens = set(self.tokens)
        return self.unique_tokens

    def process(self):
        self.tokenize()
        self.clean()
        return self.get_unique()


class Searchable:
    def __init__(self) -> None:
        self.documents: dict = {}
        self._data: dict = {}

    @property
    def document_number(self):
        return len(self.documents)

    def add_collection(self, collection: TextCollection):
        raise NotImplementedError

    def bool_search(self, token):
        raise NotImplementedError

    def bool_search_not(self, token):
        raise NotImplementedError

    def bool_search_and(self, token1, token2):
        raise NotImplementedError

    def bool_search_or(self, token1, token2):
        raise NotImplementedError


class IncidenceMatrix(Searchable):
    def __init__(self) -> None:
        super().__init__()
        self.documents: dict = {}
        self._data: dict = {}
        self._counter = Value("i", 0)

    def add_collection(self, collection: TextCollection):
        with self._counter.get_lock():
            self.documents[self._counter.value] = collection.title
            self._counter.value += 1

        for row in self._data.values():
            row.append(0)

        for word in collection.get_unique():
            if word in self._data:
                self._data[word][-1] = 1
            else:
                self._data[word] = [0 for _ in range(self.document_number - 1)] + [1]

    def bool_search(self, token):
        row = self._data.get(token)

        if not row:
            return [0 for _ in range(self.document_number)]

        return row

    def bool_search_not(self, token):
        row = self._data.get(token)

        if not row:
            return [1 for _ in range(self.document_number)]

        return [0 if col == 1 else 1 for col in row]

    def bool_search_and(self, token1, token2):
        row1 = self._data.get(token1)
        row2 = self._data.get(token2)

        if not (row1 and row2):
            return [0 for _ in range(self.document_number)]

        return [a & b for a, b in zip(row1, row2)]

    def bool_search_or(self, token1, token2):
        row1 = self._data.get(token1)
        row2 = self._data.get(token2)

        if not (row1 and row2):
            return [0 for _ in range(self.document_number)]

        return [a | b for a, b in zip(row1, row2)]

    def get_matrix(self):
        return [row for row in self._data.values()]

    def get_pretty_matrix(self):
        return self._data


class InvertedIndex(Searchable):
    def __init__(self) -> None:
        super().__init__()
        self.documents: dict = {}
        self._data: dict = {}
        self._counter = Value("i", 0)

    def add_collection(self, collection: TextCollection):
        with self._counter.get_lock():
            doc_id = self._counter.value
            self.documents[doc_id] = collection.title
            self._counter.value += 1

        for word in collection.get_unique():
            if word in self._data:
                self._data[word].append(doc_id)
            else:
                self._data[word] = [doc_id]

    def bool_search(self, token):
        row = self._data.get(token)

        if not row:
            return set()

        return row

    def bool_search_and(self, token1, token2):
        row1 = self._data.get(token1)
        row2 = self._data.get(token2)

        if not (row1 and row2):
            return []

        return list(set(row1) & set(row2))

    def bool_search_or(self, token1, token2):
        row1 = self._data.get(token1)
        row2 = self._data.get(token2)

        if not (row1 and row2):
            return []

        return list(set(row1) | set(row2))

    def bool_search_not(self, token):
        row = self._data.get(token)

        if not row:
            return list(self.documents)

        return list(set(self.documents) & set(row))

    def get_index(self):
        return self._data


def init_data(storage: Searchable):
    paths = get_collection_paths(DATA_DIR)

    for p in paths:
        collection = TextCollection(p)
        collection.process()

        storage.add_collection(collection)

    return storage
