"""The implementation of a trie data structure composed of words."""

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import Self


@dataclass
class WordTrieNode:
    """The node storing a single word in a trie (tree-like) data structure.

    Attributes:
        word: The word stored in the node.
        text: The joined words from the root of the trie.
        is_full_name: The flag indicating if the node ends a name.
        children: The child nodes of the node.
    """

    word: str = ""
    text: str = ""
    is_full_name: bool = False
    children: dict[str, Self] = field(default_factory=dict)

    @property
    def is_root(self) -> bool:
        """The flag indicating if this is a root node.

        The node is a root node if the word it stores is an empty string.
        """
        return not self.word

    @property
    def is_branching_point(self) -> bool:
        """The flag indicating if this node is a branching point.

        The node is a branching point if it has more than one child.
        """
        return len(self.children) > 1

    @property
    def is_leaf(self) -> bool:
        """The flag indicating if this is a leaf node.

        The node is a leaf node if it has no children.
        """
        return not self.children


class WordTrie:
    """The trie (tree-like) data structure storing words as nodes.

    This structure is design to effectively group strings (names) based on a
    common prefix consisting of full words.

    Attributes:
        root: The root node of the trie.
        word_delimiter: The character used to split names into words.

    Example usage:
        Define input names
        >>> names = ["foo_bar", "foo_bar_baz", "abc_asd", "abc_xyz"]
        Construct a trie from the given names using specified delimiter
        >>> trie = WordTrie.from_names(names=names, word_delimiter="_")
        Use the trie structure to group the names
        >>> trie.group_names()
        {'abc': ['abc_asd', 'abc_xyz'], 'foo_bar': ['foo_bar', 'foo_bar_baz']}
    """

    DEFAULT_WORD_DELIMITER = "_"

    def __init__(self, word_delimiter: str = DEFAULT_WORD_DELIMITER):
        self.root = WordTrieNode()
        self.word_delimiter = word_delimiter

    @classmethod
    def from_names(
        cls, names: list[str], word_delimiter: str = DEFAULT_WORD_DELIMITER
    ) -> Self:
        """Construct the trie from the given names.

        Args:
            names: The names to be inserted into the trie.
            word_delimiter: The character used to split names into words.

        Returns:
            The constructed trie.
        """
        word_trie = cls(word_delimiter=word_delimiter)
        for name in names:
            word_trie.insert_name(name)
        return word_trie

    def insert_name(self, name: str) -> None:
        """Insert the given name into the trie.

        Args:
            name: The name to be inserted into the trie.
        """
        words = name.split(self.word_delimiter)
        current_node = self.root

        for i, word in enumerate(words, 1):
            try:
                child_node = current_node.children[word]
            except KeyError:
                # The word is not in the trie - insert a new node
                text = self.word_delimiter.join(words[:i])
                child_node = WordTrieNode(word=word, text=text)
                current_node.children[word] = child_node

            current_node = child_node

        # Mark the last node as the end of the name
        current_node.is_full_name = True

    def group_names(self) -> dict[str, list[str]]:
        """Group all the names in the trie.

        The names are grouped based on their common prefixes consisting of full words.
        The resulting groups are as descriptive as possible.

        In case the given name does not share a common prefix with any other name, such
        name is grouped in an individual group. The group name is the name itself, and
        it contains only a single item - the given name. E.g. the name "foo" is added
        to the group "foo" and this group contains the single name "foo".

        Returns:
            The mapping of group names to names within each group.
        """

        def _group_names(
            node: WordTrieNode,
            # Full names in the currently traversed branch
            current_branch: list[str],
            # Sub-branches with full names for the current branching point
            current_branches: list[list[str]],
        ) -> None:
            if node.is_branching_point:
                # For each branching point, collect all full names in all sub-branches
                sub_branches: list[list[str]] = []

                # Traverse the trie recursively using DFS
                for child_node in node.children.values():
                    _group_names(
                        node=child_node,
                        # Use a new list for storing full names in each sub-branch
                        current_branch=[],
                        # Pass the reference to the list storing all sub-branches for
                        # the given branching point
                        current_branches=sub_branches,
                    )

                # Process all full names from all sub-branches for the given branching
                # point, starting from the deepest one (DFS)

                # Iterate over collected sub-branches in reverse order to allow deletion
                for branch in reversed(sub_branches):
                    if len(branch) > 1:
                        # If the given branch contains more than one full name, than
                        # the first full name is a common prefix (group) for all the
                        # following names in that branch
                        group_name = branch[0]
                        grouped_names[group_name].extend(branch)
                        # Remove processed branch
                        sub_branches.remove(branch)

                # At this point, all remaining sub-branches contain a single full name

                if node.is_root:
                    # Backtracked to the root node - all remaining full names does not
                    # share a common prefix

                    # Assumption: The names that does not share common prefix with other
                    # names should be grouped in individual groups. E.g. for the name
                    # "foo" the group name should be "foo" and this group should contain
                    # the single name "foo".
                    for full_name in chain.from_iterable(sub_branches):
                        grouped_names[full_name].append(full_name)

                elif node.is_full_name or len(sub_branches) > 1:
                    # If the branching point itself is a full name
                    # OR there are more than one sub-branch with a single full name,
                    # than the branching point is a common prefix (group) for all
                    # full names in the remaining sub-branches
                    group_name = node.text
                    if node.is_full_name:
                        # If the branching point is a full name - add it to the group
                        grouped_names[group_name].append(node.text)
                    # Add full names from all sub-branches to the group
                    grouped_names[group_name].extend(chain.from_iterable(sub_branches))

                else:
                    # If the branching point is NOT a full name
                    # AND there is only one remaining sub-branch with a single full name
                    # Add the remaining sub-branch for processing at the breaking point
                    # higher in the trie
                    current_branches.extend(sub_branches)

            else:
                if node.is_full_name:
                    # Collect only full names from the current branch
                    current_branch.append(node.text)

                if node.is_leaf:
                    # This is the end of the current branch
                    current_branches.append(current_branch)
                else:
                    # Continue traversing to the next node in the current branch
                    child_node = next(iter(node.children.values()))
                    _group_names(
                        node=child_node,
                        current_branch=current_branch,
                        current_branches=current_branches,
                    )

        grouped_names: dict[str, list[str]] = defaultdict(list)
        _group_names(self.root, [], [])

        # Return grouped names as a regular dictionary
        return dict(grouped_names)
