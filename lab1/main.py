from pathlib import Path
from typing import Generator

from word_randomizer import (
    get_collections,
    list_to_file,
    list_to_file_binary,
    pickle_list,
)

ROOT_PATH = Path("./data")
COLLECTIONS_PATH = Path("./data/collections")
PATH_RESULT_SIMPLE = Path("./data/result/simple.txt")
PATH_RESULT_BINARY = Path("./data/result/binary.txt")
PATH_RESULT_PICKLE = Path("./data/result/result.pickle")


def _count_generator(reader) -> Generator:
    """
    Helper generator function that yields reader buffer
    """

    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)


def count_lines(path: Path) -> int:
    """
    Counts lines in the specified file
    """

    with open(path, "rb") as f:
        c_generator = _count_generator(f.raw.read)

        return sum(buffer.count(b"\n") for buffer in c_generator)


def get_file_size(path: Path) -> float:
    """Returns file size in KB"""
    return path.stat().st_size / 1024


def get_unique_words(path: Path) -> set:
    with open(path, "r") as f:
        return set(f.read().splitlines())


if __name__ == "__main__":
    # get list of all word file collections
    collection_list = get_collections(COLLECTIONS_PATH)

    # get sum of all collection files
    total_size = sum(get_file_size(p) for p in collection_list)
    print(f"Total collection size: {total_size:.2f}KB")

    # general number of words
    total_words = sum(count_lines(c) for c in collection_list)
    print(f"Total number of words: {total_words}")

    # get unique words from each file and then merge it into the one global set
    unique = set()
    for path in collection_list:
        unique |= get_unique_words(path)

    print(f"Number of unique words: {len(unique)}")

    # test time of saving files
    print(
        "Time measuring (seconds):\n"
        f"\t- Simple writing: {list_to_file(unique, PATH_RESULT_SIMPLE)}\n"
        f"\t- Simple writing (binary): {list_to_file_binary(unique, PATH_RESULT_BINARY)}\n"
        f"\t- Pickle time: {pickle_list(unique, PATH_RESULT_PICKLE)}\n"
    )
