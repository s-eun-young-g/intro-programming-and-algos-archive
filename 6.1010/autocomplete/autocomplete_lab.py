"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!

# import string # optional import
# import pprint # optional import
# import typing # optional import
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    A prefix tree is a type of tree that stores an associative array
    (a mapping from keys to values). The prefix tree stores keys
    organized by their prefixes (their first characters), with
    longer prefixes given by successive levels of the prefix tree.
    Each node optionally contains a value to be associated with
    that node's prefix. Prefix trees are often used in text-processing
    applications, and so we'll limit our attention to prefix trees
    whose keys are given by strings.
    """

    def __init__(self):
        # initialize value, set None until set otherwise
        self.value = None
        # initialize children dictionary
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.

        >>> tree = PrefixTree()
        >>> tree['bat'] = 7
        >>> tree['bat']
        7
        >>> tree['bar'] = 6
        >>> tree['bar']
        6
        >>> tree[1] = True
        Traceback (most recent call last):
        ...
        TypeError
        """
        if not isinstance(key, str):
            raise TypeError  # key must be a string
        # node is self
        node = self
        for character in key:
            if character not in node.children:
                # if the character is not already a child
                # create a new node aka tree
                node.children[character] = PrefixTree()
            # move to new node
            node = node.children[character]
        # at the end of the node, set the value
        node.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.

        >>> tree = PrefixTree()
        >>> tree['bat'] = 7
        >>> tree['bat']
        7
        >>> tree['ba']
        Traceback (most recent call last):
        ...
        KeyError
        >>> tree[1]
        Traceback (most recent call last):
        ...
        TypeError

        """
        if not isinstance(key, str):
            raise TypeError  # key must be a string
        node = self
        for character in key:
            if character in node.children:
                node = node.children[character]
            else:
                # if character is not found, key doesn't exist
                raise KeyError
        if node.value is not None:
            # if node has value, return it
            return node.value
        else:
            # key exists but does not have a value
            raise KeyError

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.

        >>> tree = PrefixTree()
        >>> tree['bat'] = 1
        >>> 'bat' in tree
        True
        >>> del tree['bat']
        >>> 'bat' in tree
        False
        >>> del tree['bat']  # Key does not exist
        Traceback (most recent call last):
        ...
        KeyError
        >>> del tree[1]  # Non-string key
        Traceback (most recent call last):
        ...
        TypeError
        """
        if not isinstance(key, str):
            raise TypeError  # key must be a string
        node = self
        for character in key:
            # iterate into node
            if character in node.children:
                node = node.children[character]
            else:
                # if character is not found, key doesn't exist
                raise KeyError
        if node.value is not None:
            node.value = None  # delete key
        else:
            # key exists but does not have a value
            raise KeyError

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.

        >>> tree = PrefixTree()
        >>> tree['bat'] = 1
        >>> 'bat' in tree
        True
        >>> 'ba' in tree
        False
        >>> 1 in tree
        Traceback (most recent call last):
        ...
        TypeError
        """
        if not isinstance(key, str):
            raise TypeError  # key must be a string
        node = self
        for character in key:
            if character in node.children:
                node = node.children[character]
            else:
                # if character is not found, key isn't there
                return False
        # return True if node has value
        return node.value is not None

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values
        in this prefix tree and its children.  Must be a generator!

        >>> tree = PrefixTree()
        >>> tree['bat'] = 1
        >>> tree['bar'] = 2
        >>> tree['bark'] = 3
        >>> sorted(tree)
        [('bar', 2), ('bark', 3), ('bat', 1)]
        >>> for key, value in tree:
        ...     print(key, value)
        bar 2
        bark 3
        bat 1
        """

        def recursive_helper(node, so_far):
            """
            Helper function that recursively goes through
            the tree. Takes in the current node and the
            string created so far as arguments
            """
            # if current node has a value
            if node.value is not None:
                # yield string created so far
                # and current node value
                yield (so_far, node.value)
            for character in sorted(node.children):
                child = node.children[character]
                # add character to the string so far
                new_so_far = so_far + character
                # recursive call with new node and new so_far
                yield from recursive_helper(child, new_so_far)

        # start from original node, pass in an empty so_far
        yield from recursive_helper(self, "")


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.

    >>> text = "bat bat bar bark"
    >>> tree = word_frequencies(text)
    >>> sorted(tree)
    [('bar', 1), ('bark', 1), ('bat', 2)]
    >>> tree['bat']
    2
    >>> tree['bark']
    1
    >>> 'cat' in tree
    False
    """
    # initialize new prefix tree object
    tree = PrefixTree()

    # tokenize sentences
    sentences = tokenize_sentences(text)

    for sentence in sentences:
        # split each sentence
        words = sentence.split()
        for word in words:
            # use __contains__ method
            if word in tree:
                # if word already exists, increment its count
                # using __getitem__ and __setitem__
                tree[word] += 1
            else:
                # if word doesn't exist yet, add it to tree
                tree[word] = 1

    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.

    >>> text = "bat bat bar bark"
    >>> tree = word_frequencies(text)
    >>> autocomplete(tree, "ba", 2)
    ['bat', 'bar']
    >>> autocomplete(tree, "ba", 5)
    ['bat', 'bar', 'bark']
    >>> autocomplete(tree, "be")
    []
    >>> autocomplete(tree, 123)
    Traceback (most recent call last):
    ...
    TypeError
    """
    if not isinstance(prefix, str):
        raise TypeError  # key must be a string

    node = tree

    for character in prefix:
        # navigate through the tree to prefix node
        if character in node.children:
            node = node.children[character]
        else:
            # if the prefix isn't in tree, return empty list
            return []

    # use the __iter__ method to retrieve all (key, value)s
    # modify keys to include the prefix
    words = [(prefix + key, value) for key, value in node]

    # sort words by frequency
    words.sort(key=lambda x: -x[1])  # in descending order

    if max_count is not None:
        # if max_count is given, apply it
        words = words[:max_count]

    return [word for word, frequency in words]


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.

    >>> text = "bat bat bar bark"
    >>> tree = word_frequencies(text)
    >>> autocorrect(tree, "bar", 3)
    ['bar', 'bark', 'bat']
    >>> autocorrect(tree, "barr", 2)
    ['bar', 'bark']
    >>> autocorrect(tree, 123)
    Traceback (most recent call last):
    ...
    TypeError
    """
    if not isinstance(prefix, str):
        raise TypeError  # key must be a string

    # get autocomplete results
    autocompletes = autocomplete(tree, prefix, max_count)

    if max_count is not None:
        if len(autocompletes) >= max_count:
            # if we have enough autcomplete suggestions
            # to fill max_count, return them
            return autocompletes[:max_count]

    # if max_count is given, subtract autocompletes
    # to find number of autocorrects needed
    rest = None if max_count is None else max_count - len(autocompletes)

    # charcater set
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    # initialize list to store splits
    splits = []

    # generate all possible splits of prefix word
    for i in range(len(prefix) + 1):
        splits.append((prefix[:i], prefix[i:]))

    edits = edit_generator(
        splits, prefix, alphabet
    )  # inialize set to store autocorrected edits

    edits.discard(prefix)  # remove original prefix

    valid_edits = []
    # get edits that are valid words in the tree
    # and not already in autocompletes set
    for word in edits:
        if word in tree and word not in autocompletes:
            valid_edits.append((word, tree[word]))

    # sort valid edits by frequency in descending order
    valid_edits.sort(key=lambda x: -x[1])

    if rest is not None:
        # limit number of edits to max_count
        valid_edits = valid_edits[:rest]

    return autocompletes + [word for word, frequency in valid_edits]


def edit_generator(splits, prefix, alphabet):
    edits = set()
    # type 1: deletion edits
    for left_side, right_side in splits:
        if right_side:
            edits.add(left_side + right_side[1:])

    # type 2: transposition edits
    for i in range(len(prefix) - 1):
        edits.add(prefix[:i] + prefix[i + 1] + prefix[i] + prefix[i + 2 :])

    # type 3: substitution edits
    for left_side, right_side in splits:
        if right_side:
            for letter in alphabet:
                edits.add(left_side + letter + right_side[1:])

    # type 4: insertion edits
    for left_side, right_side in splits:
        for letter in alphabet:
            edits.add(left_side + letter + right_side)

    return edits


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.

    >>> text = "bat bat bar bark"
    >>> tree = word_frequencies(text)
    >>> word_filter(tree, "ba?")
    [('bar', 1), ('bat', 2)]
    >>> word_filter(tree, "*k")
    [('bark', 1)]
    >>> word_filter(tree, "b*t")
    [('bat', 2)]
    >>> word_filter(tree, "???")
    [('bar', 1), ('bat', 2)]
    >>> word_filter(tree, "*")
    [('bar', 1), ('bark', 1), ('bat', 2)]
    """

    results = []  # list to store matching words
    visited = set()  # visited set to keep track of entries already visited

    def match_pattern(node, word, pattern):
        if not pattern:  # if the pattern is no more
            if node.value is not None and word not in visited:
                # if word is valid, add to both results and visited
                visited.add(word)
                results.append((word, node.value))
            return
        if pattern[0] == "*":
            # skip redundant '*' in pattern
            while len(pattern) > 1 and pattern[1] == "*":
                pattern = pattern[1:]
            # scenario 1: '*' matches zero characters
            match_pattern(node, word, pattern[1:])
            # scenario 2: '*' matches one or more characters
            for char, child in node.children.items():
                match_pattern(child, word + char, pattern)
        elif pattern[0] == "?":  # check for ?
            for character, child in node.children.items():
                new_word = word + character
                match_pattern(child, new_word, pattern[1:])
        else:  # need exact character match
            character = pattern[0]
            if character in node.children:
                new_word = word + character
                match_pattern(node.children[character], new_word, pattern[1:])
            else:
                # backtrack if there is no match
                return

    # initiate pattern with empty string
    match_pattern(tree, "", pattern)

    results.sort()  # sort alphabetically

    return results


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # doctest.run_docstring_examples( # runs doctests for one function
    #    PrefixTree.__getitem__,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True
    # )
    with open("Metamorphosis.txt", encoding="utf-8") as f:
        text = f.read()
        met_tree = word_frequencies(text)
        print(f"autocomplete, gre, met: {autocomplete(met_tree, "gre", max_count = 6)}")
        print(f"filter, c*h, met: {word_filter(met_tree, "c*h")}")
    with open("Two_Cities.txt", encoding="utf-8") as f:
        text = f.read()
        cities_tree = word_frequencies(text)
        print(f"filer, r?c*t, cities: {word_filter(cities_tree, "r?c*t")}")
    with open("Alice_in_Wonderland.txt", encoding="utf-8") as f:
        text = f.read()
        alice_tree = word_frequencies(text)
        print(
            f"autocorrections, hear, alice: {autocorrect(alice_tree, "hear", max_count = 12)}"
        )
    with open("Pride_and_Prejudice.txt", encoding="utf-8") as f:
        text = f.read()
        pride_tree = word_frequencies(text)
        print(f"autocorrections, hear, pp: {autocorrect(pride_tree, "hear")}")
    with open("Dracula.txt", encoding="utf-8") as f:
        text = f.read()
        drac_tree = word_frequencies(text)
        wc = sum(1 for i in drac_tree)
        print(f"distinct words in drac: {wc}")
        total = sum(frequency for word, frequency in drac_tree)
        print(f"total words in drac: {total}")
        failure = word_filter(drac_tree, "a**")
        print(failure)
