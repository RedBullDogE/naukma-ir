import os
import pickle
from pathlib import Path
from random import choices
from time import time
from typing import Callable, Iterable, List

DIR_PATH = Path("./data/splitted/")


def timeit(func) -> Callable:
    """Decorator for time measuring"""

    def wrapper(*args, **kwargs):
        start_time = time()
        func(*args, **kwargs)
        return time() - start_time

    return wrapper


def get_collections(path: Path) -> List[Path]:
    """Get list of files containing word collections from
    the specified directory

    Args:
        path (Path): path to a directory with text files

    Returns:
        List[Path]: list of file paths
    """
    return [path / filename for filename in os.listdir(path)]


@timeit
def list_to_file(collection: Iterable[str], path: Path) -> bool:
    """Helper function for converting collection into the file by path

    Args:
        collection (Iterable[str]): collection of words
        path (Path): file path to be created

    Returns:
        bool: file created
    """
    try:
        with open(path, "w+", encoding="utf-8") as f:
            for word in collection:
                f.write(f"{word}\n")
            return True
    except IOError:
        return False


@timeit
def list_to_file_binary(collection: Iterable[str], path: Path) -> bool:
    """Helper function for converting collection into the file by path

    Args:
        collection (Iterable[str]): collection of words
        path (Path): file path to be created

    Returns:
        bool: file created
    """
    try:
        with open(path, "wb+") as f:
            for word in collection:
                f.write(word.encode("utf-8") + b"\n")
            return True
    except IOError:
        return False


@timeit
def pickle_list(collection: Iterable[str], path: Path):
    """Helper function for converting collection into the file
    by path in binary mode

    Args:
        collection (Iterable[str]): collection of words
        path (Path): file path to be created

    Returns:
        bool: file created
    """
    try:
        with open(path, "wb+") as f:
            pickle.dump(collection, f)
    except IOError:
        return False


def file_to_list(path: Path) -> list:
    """Helper function for converting file with word collection into list

    Args:
        path (Path): path to the word collection

    Returns:
        list: list of words
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def randomize_words(collection: list) -> list:
    """Helper function to randomize words from given collection.

    Function takes collection and mixes its words in random order and quantity.
    The result of this function is a list of randomly mixed words
    with the same length as input collection.

    Args:
        collection (list): input collection to be mixed

    Returns:
        list: mixed collection
    """
    return choices(collection, k=len(collection))


def randomize_collections(dir_path: Path):
    """Get all text files from directory, apply word randomizer and write them back

    Args:
        dir_path (Path): path to a directory with collections
    """
    collection_paths = get_collections(dir_path)

    for path in collection_paths:
        collection = file_to_list(path)
        words = randomize_words(collection)
        list_to_file(words, path)


if __name__ == "__main__":
    randomize_collections(DIR_PATH)
