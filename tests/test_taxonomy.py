import unittest

from src.taxonomy import add_taxonomic_item, create_taxonomy, Taxonomy, newExclusiveClassification, newInclusiveClassification
from rich.pretty import pprint


class TestTaxonomy(unittest.TestCase):
#t = create_taxonomy(name="Life")
#t1 = add_taxonomic_item(taxonomy = t, name="Flora")
#t2 = add_taxonomic_item(taxonomy = t1, name="Fauna")
#t3 = add_taxonomic_item(taxonomy = t2, name="cat", parent=t2.items[1])
#t4 = add_taxonomic_item(taxonomy = t3, name="dog", parent=t3.items[1])

    def setUp(self):
        taxo_name = "Life"
        name1 = "Flora"
        name2 = "Tulip"
        t1 = create_taxonomy(name=taxo_name)
        t2 = add_taxonomic_item(taxonomy = t1, name=name1)
        t3 = add_taxonomic_item(taxonomy = t2, name=name2, parent=t2.items[0])
        self.taxo_name = taxo_name
        self.name = name1
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

    def test_initial_state(self):
        self.assertEqual(self.t1.name, self.taxo_name)
        self.assertEqual(len(self.t1.items), 0)
        self.assertEqual(len(self.t1.first_tier), 0)
        self.assertEqual(len(self.t1.first_tier_binds), 0)
        self.assertEqual(len(self.t1.subsequent_tiers), 0)
        self.assertEqual(len(self.t1.subsequent_tier_binds), 0)
        self.assertEqual(len(self.t1.get_children()), len(self.t1.items))
        self.assertEqual(len(self.t1.get_decendents()), len(self.t1.items))


    def test_first_tier_state(self):
        self.assertEqual(self.t2.items[0].name, self.name)
        self.assertEqual(len(self.t2.items), 1)
        self.assertEqual(len(self.t2.first_tier), 1)
        self.assertEqual(len(self.t2.first_tier_binds), 1)
        self.assertEqual(len(self.t2.subsequent_tiers), 0)
        self.assertEqual(len(self.t2.subsequent_tier_binds), 0)
        self.assertEqual(self.t2.get_children(), ())
        self.assertEqual(self.t2.get_index(self.t2.items[0]), self.t2.items.index(self.t2.items[0]))
        self.assertEqual(self.t2.get_indices(self.t2.items[0]), (self.t2.items.index(self.t2.items[0]),))


    def test_subs_tier_state(self):
        self.assertEqual(self.t3.items[0].name, self.name)
        self.assertEqual(len(self.t3.items), 2)
        self.assertEqual(len(self.t3.first_tier), 1)
        self.assertEqual(len(self.t3.first_tier_binds), 1)
        self.assertEqual(len(self.t3.subsequent_tiers), 1)
        self.assertEqual(len(self.t3.subsequent_tier_binds), 1)
        self.assertEqual(self.t3.get_children(self.t3.items[0])[0], self.t3.items[1])
        self.assertEqual(self.t3.get_decendents(), self.t3.items)

class TestExclusiveClassifier(unittest.TestCase):


    def setUp(self):
        taxo_name = "Life"
        name1 = "Cat"
        name2 = "Dog"
        t1 = create_taxonomy(name=taxo_name)
        t2 = add_taxonomic_item(taxonomy = t1, name=name1)
        t3 = add_taxonomic_item(taxonomy = t2, name=name2)
        alt_taxo_name = "Vehicle"
        alt_name1 = "Car"
        alt_name2 = "Bike"
        alt_t1 = create_taxonomy(name=alt_taxo_name)
        alt_t2 = add_taxonomic_item(taxonomy = alt_t1, name=alt_name1)
        self.taxo_name = taxo_name
        self.name = name1
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.alt_t1 = alt_t1
        self.alt_t2 = alt_t2
        self.target_type = str
        self.example1 = "mittens"
        self.example2 = "fido"
        self.classifier = newExclusiveClassification(target_type = self.target_type , taxonomy = self.t3)
    
    def test_initial_state(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        self.assertEqual(self.classifier.taxonomy, self.t3)
        self.assertEqual(len(self.classifier.classified_instances), 0)
        self.assertEqual(len(self.classifier.classifications), 0)
        self.assertEqual(len(self.classifier.get_classification_indices(target=0)), 0)
    
    def test_correct_classification(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        c1 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=self.example1)
        self.assertEqual(len(c1.classified_instances), 1)
        self.assertEqual(len(c1.classifications), 1)
        self.assertEqual(len(c1.get_classification_indices(target=self.example1)), 1)
    
    def test_incorrect_classification(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        # test that an instance of the wrong type will not classify
        c1 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=5)
        self.assertEqual(len(c1.classified_instances), 0)
        self.assertEqual(len(c1.classifications), 0)
        self.assertEqual(len(c1.get_classification_indices(target=self.example1)), 0)
        # test that an instance iof the right type will not classify twice
        c2 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=self.example1)
        c3 = self.classifier.classify(taxonomic_item=c2.taxonomy.items[1], classification_target=self.example1)
        self.assertEqual(len(c3.classified_instances), 1)
        self.assertEqual(len(c3.classifications), 1)
        self.assertEqual(len(c3.get_classification_indices(target=self.example1)), 1)
        
        # test that an instanceof the right type will not classify by an arbitrary taxonomy item
        c4 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=self.example1)
        c5 = self.classifier.classify(taxonomic_item=self.alt_t2.items[0], classification_target=self.example1)
        self.assertEqual(len(c4.classified_instances), 1)
        self.assertEqual(len(c4.classifications), 1)
        self.assertEqual(len(c4.get_classification_indices(target=self.example1)), 1)


class TestInclusiveClassifier(unittest.TestCase):


    def setUp(self):
        taxo_name = "Transport"
        name1 = "People"
        name2 = "Things"
        t1 = create_taxonomy(name=taxo_name)
        t2 = add_taxonomic_item(taxonomy = t1, name=name1)
        t3 = add_taxonomic_item(taxonomy = t2, name=name2)
        alt_taxo_name = "Vehicle"
        alt_name1 = "Car"
        alt_name2 = "Bike"
        alt_t1 = create_taxonomy(name=alt_taxo_name)
        alt_t2 = add_taxonomic_item(taxonomy = alt_t1, name=alt_name1)
        self.taxo_name = taxo_name
        self.name = name1
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.alt_t1 = alt_t1
        self.alt_t2 = alt_t2
        self.target_type = str
        self.example1 = "land rover"
        self.example2 = "mini"
        self.classifier = newInclusiveClassification(target_type = self.target_type , taxonomy = self.t3)
    
    def test_initial_state(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        self.assertEqual(self.classifier.taxonomy, self.t3)
        self.assertEqual(len(self.classifier.classified_instances), 0)
        self.assertEqual(len(self.classifier.classifications), 0)
        self.assertEqual(len(self.classifier.get_classification_indices(target=0)), 0)
    
    def test_correct_classification(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        print("the beef")
        print("c1")
        c1 = self.classifier.classify(taxonomic_item=self.t3.items[0], classification_target=self.example1)
        pprint(c1)
        self.assertEqual(len(c1.classified_instances), 1)
        self.assertEqual(len(c1.classifications), 1)
        self.assertEqual(len(c1.get_classification_indices(target=self.example1)), 1)
        # test that an instance of the right type will classify twice
        c2 = c1.classify(taxonomic_item=c1.taxonomy.items[1], classification_target=self.example1)
        self.assertEqual(len(c2.classified_instances), 1) # there is only one classified instance, the landy
        self.assertEqual(len(c2.classifications), 1) # there is only one tuple of classifications
        self.assertEqual(len(c2.classifications[0]), 2) # the one tuple of classifications has two elements

        self.assertEqual(len(c2.get_classification_indices(target=self.example1)), 1) # the function only returns the one tuple of classifications
        
    
    def test_incorrect_classification(self):
        self.assertEqual(self.classifier.target_type, self.target_type)
        # test that an instance of the wrong type will not classify
        c3 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=5)
        self.assertEqual(len(c3.classified_instances), 0)
        self.assertEqual(len(c3.classifications), 0)
        self.assertEqual(len(c3.get_classification_indices(target=self.example1)), 0)

        # test that an instance of the right type will not classify by an arbitrary taxonomy item
        c4 = self.classifier.classify(taxonomic_item=self.t3.items[1], classification_target=self.example1)
        c5 = self.classifier.classify(taxonomic_item=self.alt_t2.items[0], classification_target=self.example1)
        self.assertEqual(len(c5.classified_instances), 1)
        self.assertEqual(len(c5.classifications), 1)
        self.assertEqual(len(c5.get_classification_indices(target=self.example1)), 1)
        