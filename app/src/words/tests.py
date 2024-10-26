import unittest

from .tools import group_names
from .word_trie import WordTrie

EXAMPLE_NAMES = [
    "adhoc_charge_amt",
    "adhoc_charge_amt_usd",
    "alcohol_direct_payment_ind",
    "alcohol_tax_amt",
    "alcohol_tax_amt_usd",
    "alcohol_gmv_amt",
    "alcohol_gmv_amt_usd",
    "alcohol_product_ind",
    "bag_fee",
    "bag_fee_usd",
    "bags_fee_tax_amt",
    "bags_fee_tax_amt_usd",
    "bags_in_freezer",
    "bags_in_fridge",
    "bags_in_shelves",
    "country_id",
    "currency",
]

EXPECTED_GROUPS = {
    "adhoc_charge_amt": ["adhoc_charge_amt", "adhoc_charge_amt_usd"],
    "alcohol": ["alcohol_direct_payment_ind", "alcohol_product_ind"],
    "alcohol_tax_amt": ["alcohol_tax_amt", "alcohol_tax_amt_usd"],
    "alcohol_gmv_amt": ["alcohol_gmv_amt", "alcohol_gmv_amt_usd"],
    "bag_fee": ["bag_fee", "bag_fee_usd"],
    "bags_fee_tax_amt": ["bags_fee_tax_amt", "bags_fee_tax_amt_usd"],
    "bags_in": ["bags_in_freezer", "bags_in_fridge", "bags_in_shelves"],
    "country_id": ["country_id"],
    "currency": ["currency"],
}


class WordTrieTests(unittest.TestCase):
    def _test_foo_bar_trie(self, trie):
        root_children = trie.root.children
        self.assertCountEqual(root_children.keys(), ["foo"])

        foo_node = root_children["foo"]
        self.assertEqual(foo_node.word, "foo")
        self.assertEqual(foo_node.text, "foo")
        self.assertFalse(foo_node.is_full_name)

        foo_children = foo_node.children
        self.assertCountEqual(foo_children.keys(), ["bar.baz"])

        bar_node = foo_children["bar.baz"]
        self.assertEqual(bar_node.word, "bar.baz")
        self.assertEqual(bar_node.text, f"foo{trie.word_delimiter}bar.baz")
        self.assertTrue(bar_node.is_full_name)

    def test_inserting_nodes_if_not_exist(self):
        trie = WordTrie()

        trie.insert_name(name="foo_bar.baz")

        self._test_foo_bar_trie(trie)

    def test_inserting_nodes_if_exist(self):
        trie = WordTrie()
        trie.insert_name(name="foo_bar.baz")

        # Insert the same name second time
        trie.insert_name(name="foo_bar.baz")

        self._test_foo_bar_trie(trie)

    def test_inserting_nodes_with_custom_word_delimiter(self):
        trie = WordTrie(word_delimiter="+")

        trie.insert_name(name="foo+bar.baz")

        self._test_foo_bar_trie(trie)

    def test_properties_of_nodes(self):
        trie = WordTrie()
        trie.insert_name(name="foo_bar")
        trie.insert_name(name="foo_baz")

        self.assertTrue(trie.root.is_root)
        self.assertFalse(trie.root.is_branching_point)
        self.assertFalse(trie.root.is_leaf)

        foo_node = trie.root.children["foo"]
        self.assertFalse(foo_node.is_root)
        self.assertTrue(foo_node.is_branching_point)
        self.assertFalse(foo_node.is_leaf)

        bar_node = foo_node.children["bar"]
        self.assertFalse(bar_node.is_root)
        self.assertFalse(bar_node.is_branching_point)
        self.assertTrue(bar_node.is_leaf)

    def test_constructing_trie_from_names(self):
        trie = WordTrie.from_names(names=["foo", "foo_bar", "foo_baz", "abc_xyz"])

        root_children = trie.root.children
        self.assertCountEqual(root_children.keys(), ["foo", "abc"])

        foo_node = root_children["foo"]
        self.assertCountEqual(foo_node.children.keys(), ["bar", "baz"])

        abc_node = root_children["abc"]
        self.assertCountEqual(abc_node.children.keys(), ["xyz"])

    def test_grouping_names(self):
        trie = WordTrie.from_names(names=EXAMPLE_NAMES)

        grouped_names = trie.group_names()

        self.assertEqual(grouped_names, EXPECTED_GROUPS)

    def test_grouping_names_with_custom_word_delimiter(self):
        trie = WordTrie.from_names(
            names=["foo+bar_abc", "foo+baz_xyz"], word_delimiter="+"
        )

        grouped_names = trie.group_names()

        expected_groups = dict(foo=["foo+bar_abc", "foo+baz_xyz"])
        self.assertEqual(grouped_names, expected_groups)


class GroupNamesTests(unittest.TestCase):
    def test_grouping_names(self):
        grouped_names = group_names(names=EXAMPLE_NAMES)

        self.assertEqual(grouped_names, EXPECTED_GROUPS)


if __name__ == "__main__":
    unittest.main()
