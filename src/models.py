from pydantic import BaseModel, ValidationError, validator, Field, root_validator
from typing import Union, Literal
from enum import Enum, Flag, auto


class GRAPH(Flag):

    def __new__(cls, singular, plural):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__) + 1
        obj._name_ = singular
        obj.singular = singular
        obj.plural = plural
        return obj

    THING = "thing", "things"
    COMPOSITION = "composition", "compositions"
    MATERIAL = "material", "materials"
    EMBODIMENT = "embodiement", "embodiments"
    PROVENANCE = "provenance", "provenances"
    OPERATION = "operation", "operations"
    CORRESPONDANCE = "correspondance", "correspondances"
    SYSTEM = "system", "systems"
    PASSIVITY = "passivity", "passivities"
    ACTIVITY = "activity", "activities"
    INFLUENCE = "influence", "influences"


    @classmethod
    def singularsTuple(cls):
        return [item.singular for item in cls]

    @classmethod
    def pluralsTuple(cls):
        return [item.plural for item in cls]
    
    @classmethod
    def toDict(cls):
        return dict(zip(cls.singularsTuple(), cls.pluralsTuple(),))

    @classmethod
    def toTuple(cls):
        return tuple(zip(cls.singularsTuple(), cls.pluralsTuple(),))
    


NODES = GRAPH.THING | GRAPH.MATERIAL | GRAPH.SYSTEM
RELATIONSHIPS = GRAPH.COMPOSITION | GRAPH.PROVENANCE | GRAPH.OPERATION | GRAPH.CORRESPONDANCE | GRAPH.PASSIVITY | GRAPH.ACTIVITY | GRAPH.INFLUENCE
HIGHER = GRAPH.SYSTEM | GRAPH.CORRESPONDANCE | GRAPH.ACTIVITY | GRAPH.INFLUENCE


class Thing(BaseModel):
    name: str


class Material(BaseModel):
    name: str




class Composition(BaseModel):
    of: Thing
    by: Thing

    @validator('by')
    def composition_loop(cls, v, values):
        if v == values['of']:
            raise ValueError('A thing must not be composed of itself')
        return v


class Embodiment(BaseModel):
    of: Thing
    by: Material


class Provenance(BaseModel):
    of: Thing # e.g a good
    by: Thing # e.g. a truck

    @root_validator
    def act_loop(cls, values):
        if values['of'] == values['by']:
            raise ValueError('A thing must not be acted upon by itself')
        return values


class Operation(BaseModel):
    of: Thing # e.g. a truck
    by: Thing # e.g. fuel

    @root_validator
    def act_loop(cls, values):
        print("values", values)
        if values['of'] == values['by']:
            raise ValueError('A thing must not act upon itself')
        return values


class ProvOpCorrespondance(BaseModel):
    provenance: Provenance
    operation: Operation
    
    @root_validator
    def correspondance_integrity(cls, values):
        if not values['provenance'].by == values['operation'].of:
            raise ValueError('The provenance by-thing does not match the operation of-thing')
        return values
    

class System(BaseModel):
    name: str


class Passivity(BaseModel):
    influence_type: Literal['Passivity']    
    of: Thing
    by: Thing



class Activity(BaseModel):
    influence_type: Literal['Activity']
    of: Thing
    by: Thing
    operations: list[Operation] # should there be two types of influence - active and passive, the latter without ops?

    @root_validator
    def operation_integrity(cls, values):
        for op in values['operations']:
            if not op.of == values['of']:
                raise ValueError('An operation is included where the operations\' operating-thing does not match the activity influencing-thing')
        return values
    #todo validate operation

class Influence(BaseModel):
    system: System
    containing: Union[Activity | Passivity] = Field(..., discriminator='influence_type')


class Domain(BaseModel):
    things: tuple[Thing, ...] = [] # the total of things
    materials: tuple[Material, ...] = [] # the total of materials
    embodiments: tuple[Embodiment, ...] = [] # the total thing-material embodiment relationships
    materialisation: tuple[Thing, ...] = [] # the total of things which are embodied
    compositions: tuple[Composition, ...] = [] # the total of thing-thing composition relationships
    systems: tuple[System, ...] = [] # the total of systems
    provenances: tuple[Provenance, ...] = [] # the total of thing-thing influence relationships in systems
    operations: tuple[Operation, ...] = [] # the total of thing-thing influence relationships in systems
    correspondances: tuple[ProvOpCorrespondance, ...] = [] # the total of provenance-operation correspondances
    influences: tuple[Influence, ...] = [] # the total of thing-thing influence relationships in systems


def newDomain():
    return Domain(
        things = (),
        materials = (),
        embodiments = (),
        materialisation = (),
        compositions = (),
        systems = (),
        provenances = (),
        operations = (),
        correspondences = (),
        influences = (),

)


def createNode(node: NODES, name: str):
    match node:
        case GRAPH.THING:
            return Thing(name=name)
        case GRAPH.MATERIAL:
            return Material(name=name)
        case GRAPH.SYSTEM:
            return System(name=name)


def addNode(domain: Domain, element: GRAPH, name: str):
    if element in NODES:
        plurals = GRAPH.pluralsTuple()
        domain_dump = domain.dict(exclude={element.plural})
        nodes_dump = domain.dict(include={element.plural})
        node = createNode(node = element, name = name)
        new_things = nodes_dump[element.plural] + (node,)
        data_dict = domain_dump | {element.plural: new_things}
        return Domain(**data_dict)
    else:
        return domain


def addThing(domain: Domain, name: str):
    return addNode(domain = domain, element = GRAPH.THING, name = name)


def addMaterial(domain: Domain, name: str):
    return addNode(domain = domain, element = GRAPH.MATERIAL, name = name)


def addSystem(domain: Domain, name: str):
    return addNode(domain = domain, element = GRAPH.SYSTEM, name = name)



        
    

def addProvenance(domain: Domain, of: Thing, by: Thing):
    return Domain(
        things = domain.things, 
        materials = domain.materials,
        embodiments = domain.embodiments,
        materialisation = domain.materialisation,
        compositions = domain.compositions,
        provenances = domain.provenances + (Provenance(
            of = of,
            by = by,
        ),),
        operations = domain.operations,
        correspondences = domain.correspondances, 
        systems = domain.systems,
        influences = domain.influences
        )


def addOperation(domain: Domain, of: Thing, by: Thing):
    return Domain(
        things = domain.things, 
        materials = domain.materials,
        embodiments = domain.embodiments,
        materialisation = domain.materialisation,
        compositions = domain.compositions,
        provenances = domain.provenances,
        operations = domain.operations + (Operation(
            of = of,
            by = by,
        ),),
        correspondences = domain.correspondances, 
        systems = domain.systems,
        influences = domain.influences
        )


def addPassiveInfluence(domain: Domain, system: System, of: Thing, by: Thing):
    return Domain(
        things = domain.things, 
        materials = domain.materials,
        embodiments = domain.embodiments,
        materialisation = domain.materialisation,
        compositions = domain.compositions,
        systems = domain.systems, 
        provenances = domain.provenances,
        operations = domain.operations,
        correspondences = domain.correspondances, 
        influences = domain.influences + (Influence(
            system = system,
            containing = Passivity(
                influence_type = "Passivity",
                of = of,
                by = by,
            )
        ),)
    )


def addActiveInfluence(domain: Domain, system: System, of: Thing, by: Thing, operations: list[Operation]):
    return Domain(
        things = domain.things, 
        materials = domain.materials,
        embodiments = domain.embodiments,
        materialisation = domain.materialisation,
        compositions = domain.compositions,
        systems = domain.systems, 
        provenances = domain.provenances,
        operations = domain.operations,
        correspondences = domain.correspondances, 
        influences = domain.influences + (Influence(
            system = system,
            containing = Activity(
                influence_type = "Activity",
                of = of,
                by = by,
                operations = operations
            )
        ),)
    )


def composeThing(domain: Domain, of: Thing, by: Thing):
    if not of in domain.things:
        return domain
    if not by in domain.things:
        return domain
    return Domain(
        things = domain.things, 
        materials = domain.materials,
        embodiments = domain.embodiments,
        materialisation = domain.materialisation,
        compositions = domain.compositions + (Composition(
            of = of,
            by = by,
            ),),
        systems = domain.systems, 
        provenances = domain.provenances,
        operations = domain.operations,
        correspondences = domain.correspondances, 
        influences = domain.influences
    )


def embodyThing(domain: Domain, of: Thing, by: Material):
    if of in domain.materialisation:
        return domain
    if not of in domain.things:
        return domain
    if not by in domain.materials:
        return domain
    return Domain(
        things = domain.things,
        materials = domain.materials,
        embodiments = domain.embodiments + (Embodiment(
            of = of,
            by = by
            ),),
        materialisation = domain.materialisation + (by,),
        compositions = domain.compositions,
        correspondences = domain.correspondances,
        provenances = domain.provenances,
        operations = domain.operations,
        systems = domain.systems,
        influences = domain.influences
        )
    
