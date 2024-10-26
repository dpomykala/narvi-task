from .word_trie import WordTrie

# Note: In the exercise description the expected output is stated as "json object".
# I'm not sure if the intention was actually an encoded JSON object or just a python
# dictionary. I decided to return a plain dict here for more flexibility and encode
# to JSON later when needed.


def group_names(
    names: list[str], word_delimiter: str = WordTrie.DEFAULT_WORD_DELIMITER
) -> dict[str, list[str]]:
    """Group all the given names based on their prefixes.

    Internally, a trie data structure is used to perform grouping. For details,
    see the docstring for the word_trie.WordTrie.group_names method.

    Args:
        names: The names to be grouped.
        word_delimiter: The character used to split names into words.

    Returns:
        The mapping of group names to names within each group.
    """
    trie = WordTrie.from_names(names=names, word_delimiter=word_delimiter)
    return trie.group_names()
