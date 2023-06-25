from pydantic import BaseModel, ValidationError, validator


class Thing(BaseModel):
    name: str


class Domain(BaseModel):
    things: list[Thing]
    materialisation: list[int]



class Composition(BaseModel):
    of: Thing
    by: Thing

    @validator('by')
    def composition_loop(cls, v, values):
        if v == values['of']:
            raise ValueError('A thing must not be composed of itself')
        return v


class Material(BaseModel):
    name: str


class Embodiment(BaseModel):
    thing: Thing
    material: Material


#def embody(thing: Thing, material: Material):
#    try:
#        thing_index = ThingRelationshpRegistry.things.index(thing)
#        
#    except ValueError:
#        print("That thing does not exist")
#    if 


class Provenance(BaseModel):
    thing: Thing
    actor: Thing

    @validator('actor')
    def act_loop(cls, v, values):
        if v == values['thing']:
            raise ValueError('A thing must not be acted upon by itself')
        return v

class Operation(BaseModel):
    thing: Thing
    acted: Thing

    @validator('acted')
    def act_loop(cls, v, values):
        if v == values['thing']:
            raise ValueError('A thing must not act upon by itself')
        return v

class System(BaseModel):
    name: str


class Influence(BaseModel):
    system: System
    of: Thing
    on: Thing
    operations: list[Operation]

    @validator('operations')
    def operation_integrity(cls, v, values):
        for op in v:
            if not op.thing == values['of']:
                raise ValueError('An operation is included where the operating-thing does not match the influencing-thing')
        return v