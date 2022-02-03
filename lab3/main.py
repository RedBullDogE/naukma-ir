from pathlib import Path
import string
from lab2.helpers import get_collection_paths

from lab2.main import CollectionException
from nltk.tokenize import word_tokenize


DATA_DIR = Path("./data")
CLOSE_WORDS_PARAM = 5


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

    def get_tokens(self):
        return self.tokens

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


class DoubleWordIndex(Searchable):
    def __init__(self) -> None:
        super().__init__()
        self.documents: dict = {}
        self._data: dict = {}
        self._data_pairs: dict = {}
        self._counter = 0

    def add_collection(self, collection: TextCollection):
        doc_id = self._counter
        self.documents[doc_id] = collection.title
        self._counter += 1

        for word in collection.get_unique():
            if word in self._data:
                self._data[word].append(doc_id)
            else:
                self._data[word] = [doc_id]

        for word1, word2 in zip(
            collection.get_tokens()[:-1], collection.get_tokens()[1:]
        ):
            if (word1, word2) in self._data_pairs:
                self._data_pairs[(word1, word2)].add(doc_id)
            else:
                self._data_pairs[(word1, word2)] = set((doc_id,))

    def search(self, token):
        return self._data.get(token, [])

    def search_phrase(self, token1, token2):
        return (
            self._data_pairs.get((token1, token2))
            or self._data_pairs.get((token2, token1), set())
        )


class CoordinateInvertedIndex(Searchable):
    def __init__(self) -> None:
        super().__init__()
        self.documents: dict = {}
        self._data: dict = {}
        self._counter = 0

    def add_collection(self, collection: TextCollection):
        doc_id = self._counter
        self.documents[doc_id] = collection.title
        self._counter += 1

        for pos, word in enumerate(collection.get_tokens()):
            if word in self._data:
                if doc_id in self._data[word]:
                    self._data[word][doc_id].append(pos)
                else:
                    self._data[word][doc_id] = [pos]
            else:
                self._data[word] = {doc_id: [pos]}

    def search(self, token):
        return self._data.get(token, {})

    def search_phrase(self, token1, token2):
        meta1 = self.search(token1)
        meta2 = self.search(token2)

        filtered = {k: (v, meta2[k]) for k, v in meta1.items() if k in meta2}

        results = {}
        for doc, pos in filtered.items():
            results[doc] = sorted(
                [
                    (a, b, abs(a - b))
                    for a in pos[0]
                    for b in pos[1]
                    if abs(a - b) < CLOSE_WORDS_PARAM
                ],
                key=lambda el: el[-1],
            )

        return results


def init_data(storage: Searchable):
    paths = get_collection_paths(DATA_DIR)

    for p in paths:
        collection = TextCollection(p)
        collection.process()

        storage.add_collection(collection)

    return storage