from pydantic import BaseModel, create_model, ValidationError, validator, Field, root_validator
from typing import Union, Optional, Type, Any, overload


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

    def name(self):
        return self.taxonomy_head.name
    
    @overload
    def get_children(self):
        return self.first_tier
    
    @overload
    def get_children(self, target: TaxonomicItem):
        for item in self.items:
            if item == target:
                children = []
                for sub in self.subsequent_tier_bind:
                    if sub.parent == target:
                        children.add(sub.child)
                return tuple(children)
        return ()

    

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
    print(item)
    return Taxonomy(
        taxonomy_head = TaxonomyHead(
            name = taxonomy.name()
        ),
        items = taxonomy.items + (item,),
        first_tier = taxonomy.first_tier if parent else taxonomy.first_tier + (len(taxonomy.items) + 1,),
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


class ExclusiveClassifier(BaseModel):
    target_type: Type
    taxonomy: Taxonomy
    classified_instances: tuple[Any, ...] = ()
    classifications: tuple[int, ...] = ()


    @root_validator
    def type_match(cls, values):
        for item in values['classified_instances']:
            if not isinstance(item, values['target_type']):
                raise ValueError('A type instance has been included which does not match the target type')
        return values
    
    def classify(self, taxonomic_item: TaxonomicItem, classification_target: Type):
        if not isinstance(classification_target, self.target_type):
            return self
        if classification_target in self.classified_instances:
            return self
        try:
            taxonomy_index = self.taxonomy.items.index(taxonomic_item)
            return ExclusiveClassifier(
                target_type = self.target_type,
                taxonomy = self.taxonomy,
                classified_instances = self.classified_instances + (classification_target,),
                classifications = self.classifications + (taxonomy_index,),
            )
        except IndexError:
            return self

def newExclusiveClassification(target_type: Type, taxonomy: Taxonomy):
    return ExclusiveClassifier(
        target_type = target_type,
        taxonomy = taxonomy,
        classified_instances = (),
        classifications = (),
    )