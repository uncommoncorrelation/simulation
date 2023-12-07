import unittest

from src.taxonomy import add_taxonomic_item, create_taxonomy, Taxonomy


class TestTaxonomy(unittest.TestCase):
#t = create_taxonomy(name="Life")
#t1 = add_taxonomic_item(taxonomy = t, name="Flora")
#t2 = add_taxonomic_item(taxonomy = t1, name="Fauna")
#t3 = add_taxonomic_item(taxonomy = t2, name="cat", parent=t2.items[1])
#t4 = add_taxonomic_item(taxonomy = t3, name="dog", parent=t3.items[1])

    def setUp(self):
        taxo_name = "Life"
        name1 = "Flora"
        name2 = "Rose"
        t1 = create_taxonomy(name=taxo_name)
        t2 = add_taxonomic_item(taxonomy = t1, name=name1)
        t3 = add_taxonomic_item(taxonomy = t2, name=name2, parent=t2.items[0])
        self.taxo_name = taxo_name
        self.name = name1
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

    def define_initial_state(self):
        return (0,0,0,0,0,)

    def define_first_state(self, items_count: int, first_count: int):
        subs_count = items_count - first_count
        return (items_count, first_count, first_count, subs_count, subs_count,)

    def define_subs_state(self, items_count: int, subs_count: int):
        first_count = items_count - subs_count
        return (items_count, first_count, first_count, subs_count, subs_count,)

    def test_initial_state(self):
        self.assertEqual(self.t1.name, self.taxo_name)
        self.assertEqual(len(self.t1.items), 0)
        self.assertEqual(len(self.t1.first_tier), 0)
        self.assertEqual(len(self.t1.first_tier_binds), 0)
        self.assertEqual(len(self.t1.subsequent_tiers), 0)
        self.assertEqual(len(self.t1.subsequent_tier_binds), 0)
        self.assertEqual(len(self.t1.get_children()), len(self.t1.items))


    def test_first_tier_state(self):
        self.assertEqual(self.t2.items[0].name, self.name)
        self.assertEqual(len(self.t2.items), 1)
        self.assertEqual(len(self.t2.first_tier), 1)
        self.assertEqual(len(self.t2.first_tier_binds), 1)
        self.assertEqual(len(self.t2.subsequent_tiers), 0)
        self.assertEqual(len(self.t2.subsequent_tier_binds), 0)
        self.assertEqual(self.t2.get_children(), ())

    def test_subs_tier_state(self):
        self.assertEqual(self.t3.items[0].name, self.name)
        self.assertEqual(len(self.t3.items), 2)
        self.assertEqual(len(self.t3.first_tier), 1)
        self.assertEqual(len(self.t3.first_tier_binds), 1)
        self.assertEqual(len(self.t3.subsequent_tiers), 1)
        self.assertEqual(len(self.t3.subsequent_tier_binds), 1)
        print("Childs: ", self.t3.get_children(self.t3.items[0]))
        self.assertEqual(self.t3.get_children(self.t3.items[0])[0], self.t3.items[1])
