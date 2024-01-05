from pydantic import BaseModel, create_model, ValidationError, validator, Field, root_validator
from typing import Union, Optional, Type, Any, overload
from itertools import repeat
from rich.pretty import pprint


class TaxonomyHead(BaseModel):
    name: str


class TaxonomicItem(BaseModel):
    name: str


class FirstTierBind(BaseModel):
    taxonomy: TaxonomyHead
    child: TaxonomicItem


class SubsequentTierBind(BaseModel):
    parent: TaxonomicItem
    child: TaxonomicItem


class Taxonomy(BaseModel):
    taxonomy_head: TaxonomyHead
    items: tuple[TaxonomicItem, ...] = ()
    first_tier: tuple[int, ...] = ()
    first_tier_binds: tuple[FirstTierBind, ...] = ()
    subsequent_tiers: tuple[int, ...] = ()
    subsequent_tier_binds: tuple[SubsequentTierBind, ...] = ()
    #children_map: tuple[tuple[int,...], ...] TODO
    
    @property
    def name(self):
        return self.taxonomy_head.name
    
    @property
    def items_count(self):
        return len(self.items)

    @property
    def first_tier_items_count(self):
        return len(self.first_tier)

    @property
    def subsequent_tier_items_count(self):
        return len(self.subsequent_tiers)
    
    @root_validator
    def state_check(cls, values):
        if len(values['items']) != (len(values['first_tier']) + (len(values['subsequent_tiers']))):
            raise ValueError('The state of the taxonomy is corrupted, the total items do not match the sum of entries for first and subsequent tiers')
        return values
    
    @overload
    def get_children(self):
        ...
    
    def get_children(self, target: Optional[TaxonomicItem] = None):
        if target == None:
            # Early return to to supply the two simple cases: initial and first tier
            return self.items[self.first_tier[0]: self.first_tier[-1]] if len(self.items) else ()
        def targetter(sub, target):
            if sub.parent == target:
                return sub.child
        return tuple(map(targetter, self.subsequent_tier_binds, repeat(target,)))

    def get_decendents(self, target: Optional[TaxonomicItem] = None):
        if target == None:
            # Early return to to supply the two simple cases: initial and first tier
            return self.items
        return tuple(map(self.get_children, self.items))
    
    def get_index(self, target: TaxonomicItem):
        try: 
            return (self.items.index(target),)
        except ValueError:
            return ()
 
    def get_indices(self, *targets: TaxonomicItem):
        targets = targets
        return tuple(map((self.get_index)[0], targets))


def create_taxonomy(name: str):
    return Taxonomy(
        taxonomy_head = TaxonomyHead(
            name = name
        ),
        items = (),
        first_tier = (),
        first_tier_binds = (),
        subsequent_tiers = (),
        subsequent_tier_binds =(),
        )


def add_taxonomic_item(taxonomy: Taxonomy, name: str, parent: Optional[TaxonomicItem] = None):
    if parent != None:
        if parent not in taxonomy.items:
            # Early return to stop a taxonomy from becoming corrupted with items from other taxonomies
            return taxonomy
    item = TaxonomicItem(name = name)
    return Taxonomy(
        taxonomy_head = TaxonomyHead(
            name = taxonomy.name
        ),
        items = taxonomy.items + (item,),
        first_tier = taxonomy.first_tier if parent else taxonomy.first_tier + (len(taxonomy.items) + 1,) if len(taxonomy.items) else (0,),
        first_tier_binds = taxonomy.first_tier_binds if parent else taxonomy.first_tier_binds + (
            FirstTierBind(
                taxonomy = taxonomy.taxonomy_head,
                child = item 
            ),),
        subsequent_tiers = taxonomy.subsequent_tiers if not parent else taxonomy.subsequent_tiers + (len(taxonomy.items) + 1,),
        subsequent_tier_binds = taxonomy.subsequent_tier_binds if not parent else taxonomy.subsequent_tier_binds + (
            SubsequentTierBind(
                parent = parent,
                child = item 
            ),),
        )


class BaseClassifier(BaseModel):
    """
    The classifier is a datatype which binds instances of a given type, to a taxonomic structure.
    """
    target_type: Type
    taxonomy: Taxonomy
    classified_instances: tuple[Any, ...] = ()

    @root_validator
    def type_match(cls, values):
        for item in values['classified_instances']:
            if not isinstance(item, values['target_type']):
                raise ValueError('A type instance has been included which does not match the target type')
        return values


class ExclusiveClassifier(BaseClassifier):
    # the index of a classification should match the index of the classified instance
    # the ints are the index position of the taxonomy item
    classifications: tuple[int, ...] = ()

    def get_classification_indices(self, target: Any):
        try:
            instance_index = self.classified_instances.index(target)
            return (self.classifications[instance_index],)
        except ValueError:
            return ()

    @root_validator
    def exclusivity(cls, values):
        for item in values['classified_instances']:
            if values['classified_instances'].count(item) > 1:
                raise ValueError('A type instance has been included which is already present in a classification')
        return values
    
    def classify(self, taxonomic_item: TaxonomicItem, classification_target: Type):
        if not isinstance(classification_target, self.target_type): # Type exclusivity protector
            return self
        if classification_target in self.classified_instances: # Classification exclusivity protector
            return self
        try:
            taxonomy_index = self.taxonomy.items.index(taxonomic_item)
            return ExclusiveClassifier(
                target_type = self.target_type,
                taxonomy = self.taxonomy,
                classified_instances = self.classified_instances + (classification_target,),
                classifications = self.classifications + (taxonomy_index,),
            )
        except ValueError: # Catches wrong Taxonomic items for this classification structure
            return self

def newExclusiveClassification(target_type: Type, taxonomy: Taxonomy):
    return ExclusiveClassifier(
        target_type = target_type,
        taxonomy = taxonomy,
        classified_instances = (),
        classifications = (),
    )

class InclusiveClassifier(BaseClassifier):
    """
    The classifier is a datatype which binds instances of a given type, to a taxonomic structure.
    """
    # the index of a tuple of classifications should match the index of the classified instance
    # the ints are the index position of the taxonomy item

    classifications: tuple[tuple[int, ...], ...] = ()

    def get_classification_indices(self, target: Any):
        try:
            instance_index = self.classified_instances.index(target)
            return (self.classifications.index(self.classifications[instance_index]),)
        except ValueError:
            return ()

    @root_validator
    def type_match(cls, values):
        for item in values['classified_instances']:
            if not isinstance(item, values['target_type']):
                raise ValueError('A type instance has been included which does not match the target type')
        return values
    
    def classify(self, taxonomic_item: TaxonomicItem, classification_target: Type):
        if not isinstance(classification_target, self.target_type): # Type exclusivity protector
            print("type excl check")
            return self
        try:
            taxonomy_index = self.taxonomy.get_index(taxonomic_item)
            print("classification target", classification_target)
            print("taxo indec", taxonomy_index)

            if len(self.classifications) == 0:
                # here we know this is a first classification
                # therefore we create the first classification tuple, at position 0 in the classifications tuple
                print("lenth check passes")
                return InclusiveClassifier(
                    target_type = self.target_type,
                    taxonomy = self.taxonomy,
                    classified_instances = (classification_target,),
                    classifications = ((taxonomy_index[0],),)
                )  
            classification_index = self.get_classification_indices(classification_target)      
            if len(classification_index) > 0:      
                # here we know this is a subsequent classification of an already classified instance
                # therefore we must find the correct classification tuple for the classified instance
                # this classification tuple must be add/updated to include the index position of the newly applied taxonomy item
                
                print("class indec", classification_index)
                new_classification_index = classification_index + (taxonomy_index[0],)
                print(new_classification_index)
                # get everything up to the target index, otherwise empty tuple
                initial_slice = self.classifications[: classification_index[0]] if len(self.classifications) > 0 else ()
                print(initial_slice)
                # get everything after the target index, otherwise empty tuple
                final_slice = self.classifications[classification_index[0] + 1 :] if len(self.classifications) > (classification_index[0] + 1) else ()
                print(final_slice)

                rebuild1 = (initial_slice + new_classification_index) if initial_slice != () else ((new_classification_index),)
                rebuild2 = rebuild1 + (final_slice,) if final_slice != () else rebuild1
                pprint(rebuild2)
                return InclusiveClassifier(
                    target_type = self.target_type,
                    taxonomy = self.taxonomy,
                    classified_instances = self.classified_instances,
                    classifications = rebuild2,
                )
        except IndexError: # Catches wrong Taxonomic items for this classification structure
            print("wrong taxo check")
            return self

def newInclusiveClassification(target_type: Type, taxonomy: Taxonomy):
    return InclusiveClassifier(
        target_type = target_type,
        taxonomy = taxonomy,
        classified_instances = (),
        classifications = (),
    )

