import unittest

from src.taxonomy import add_taxonomic_item, create_taxonomy, Taxonomy

taxo_name = "Life"

class TestTaxonomy(unittest.TestCase):
#t = create_taxonomy(name="Life")
#t1 = add_taxonomic_item(taxonomy = t, name="Flora")
#t2 = add_taxonomic_item(taxonomy = t1, name="Fauna")
#t3 = add_taxonomic_item(taxonomy = t2, name="cat", parent=t2.items[1])
#t4 = add_taxonomic_item(taxonomy = t3, name="dog", parent=t3.items[1])

    def setUp(self):
        self.taxonomy = create_taxonomy(name=taxo_name)

    def test_taxo_name(self):
        self.assertEqual(self.taxonomy.name(), taxo_name)
    
    def test_first_child(self):
        t1 = add_taxonomic_item(taxonomy = self.taxonomy, name="Flora")
        self.assertTrue(len(t1.items), 1)

