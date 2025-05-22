# Useful descriptors

This module defines three Python descriptors : ``Alias``, ``OperableProperty`` and ``Result``:
- ``Alias`` is designed to create an alias of a method or attribute of a class,
- ``OperableProperty`` and ``Result`` are designed to work together to create simple properties of a class

## Tutorial

### ``Alias``

This descriptor is designed to create an alias of a method or attribute of a class. It is used as follows:


```python
from descriptors import Alias

class A:
    def __init__(self, val):
        self.val = val

    alias_of_val = Alias('val')

a = A(1)
print(f"{a.val = }")
print(f"{a.alias_of_val = }")
```

    a.val = 1
    a.alias_of_val = 1
    

The alias changes when the attribute changes:


```python
a.val = 2
print(f"{a.alias_of_val = }")
```

    a.alias_of_val = 2
    

The alias can also be set:


```python
a.alias_of_val = 3
print(f"{a.val = }")
```

    a.val = 3
    

Finally, deleting the attribute also deletes the alias:


```python
del a.val
try:
    print(f"{a.alias_of_val = }")
except AttributeError as e:
    print(e)
```

    'A' object has no attribute 'val'
    

In addition, an alias of a method can be defined in the same way:


```python
class B:
    def method(self, a):
        return a

    alias_of_method = Alias('method')

b = B()
print(f"{b.alias_of_method(1) = }")
```

    b.alias_of_method(1) = 1
    

Finally, it is possible to create an alias of a nested value:


```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class FamilyMember:
    name: str
    father: Optional['FamilyMember'] = None # Quoted to prevent circular definition
    mother: Optional['FamilyMember'] = None

    paternal_grandmother = Alias('father.mother')

Shmi_Skywalker = FamilyMember('Shmi Skywalker')
Anakin_Skywalker = FamilyMember('Anakin Skywalker', mother=Shmi_Skywalker)
Luke_Skywalker = FamilyMember('Luke Skywalker', father=Anakin_Skywalker)

print(f"{Luke_Skywalker.paternal_grandmother = }")
```

    Luke_Skywalker.paternal_grandmother = FamilyMember(name='Shmi Skywalker', father=None, mother=None)
    

### ``OperableProperty`` and ``Result``

These two descriptors allow the creation of attributes that are the result of an operation on other attributes of the class. This is already possible in Python using the ``@property`` decorator, but these descriptors make these definitions more readable and less boilerplate for simple cases. In the following example, a similar behaviour is implemented twice, once using the ``@property`` decorator and once using the descriptors defined in this module.

#### Example
First, using ``@property``


```python
class C:
    
    def __init__(self, c1, c2, c3):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3

    @property
    def c4(self):
        return self.c1 * self.c2

    @property
    def c5(self):
        return self.c2 + self.c3

    @property
    def c6(self):
        return self.c3 / self.c1

c = C(c1 = 1, c2 = 2, c3 = 3)
print(f"{c.c4 = }")
print(f"{c.c5 = }")
print(f"{c.c6 = }")
```

    c.c4 = 2
    c.c5 = 5
    c.c6 = 3.0
    

Second, using ``OperableProperty``:


```python
from descriptors import OperableProperty # Result doesn't have to be imported for most applications

class D:
    d1 = OperableProperty()
    d2 = OperableProperty()
    d3 = OperableProperty()
    
    def __init__(self, d1, d2, d3):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3

    d4 = d1 * d2
    d5 = d2 + d3
    d6 = d3 / d1

d = D(d1 = 1, d2 = 2, d3 = 3)
print(f"{d.d4 = }")
print(f"{d.d5 = }")
print(f"{d.d6 = }")
```

    d.d4 = 2
    d.d5 = 5
    d.d6 = 3.0
    

Also, these descriptors are compatble with the ``@dataclass`` decorator:


```python
from dataclasses import dataclass

@dataclass
class E:
    e1: OperableProperty = OperableProperty()
    e2: OperableProperty = OperableProperty()
    e3: OperableProperty = OperableProperty()

    e4 = e1 * e2
    e5 = e2 + e3
    e6 = e3 / e1

e = E(e1 = 1, e2 = 2, e3 = 3)
print(f"{e.e4 = }")
print(f"{e.e5 = }")
print(f"{e.e6 = }")
```

    e.e4 = 2
    e.e5 = 5
    e.e6 = 3.0
    

Here, these two examples are just as long, but in practical applications the second example is more easily readable, especially if the number of properties is high.

It is worth noting that:
- It is possible to chain operations,
- It is possible to reference the result of an expression in another expression,
- Numbers and other values can be used in an expression.


```python
from datetime import datetime

@dataclass
class Person:
    first_name: str = OperableProperty()
    last_name: str = OperableProperty()
    date_of_birth: datetime = OperableProperty()
    
    name = first_name + ' ' + last_name
    # two additions are chained : no issue
    # ' ' is a constant, no issue
    
    age = datetime.now() - date_of_birth
    # Most types that support common operators are fine

    nickname = name + ' a.k.a. Darth Vader'
    # Reference to name, which is already defined by an expression
    
    
p = Person(
    first_name='Anakin', 
    last_name='Skywalker', 
    date_of_birth=datetime(year=1999, month=10, day=13)
)
print(f'{p.name = }')
print(f'{p.nickname = }')
print(f'{p.age = }') # This timedelta is not pretty but it works
```

    p.name = 'Anakin Skywalker'
    p.nickname = 'Anakin Skywalker a.k.a. Darth Vader'
    p.age = datetime.timedelta(days=9353, seconds=77033, microseconds=957460)
    

### Inheritance

The behaviour of the decscriptors is slightly modified in case of class inheritance.
- The ``OperableProperty`` of the parent class must be accessed via the parent class itself
- The properties that have to be defined by the child class can be accessed by using a string starting with '@' (hardcoded). This raises an error if the property is accessed, but it doesn't prevent the class from being instanced.

Example:


```python
@dataclass
class LightSaber:
    owner: str = OperableProperty()

    # Access RedSaber.color using '@color'
    exclamation = owner + ' wields a ' + '@color' + ' lightsaber !'

class RedSaber(LightSaber):
    color = 'red'

    # Access LightSaber.owner by name
    interrogation = "Is That " + LightSaber.owner + "'s saber ?"

vador_saber = RedSaber('Darth Vador')

print(f'{vador_saber.exclamation = }')
print(f'{vador_saber.interrogation = }')
```

    vador_saber.exclamation = 'Darth Vador wields a red lightsaber !'
    vador_saber.interrogation = "Is That Darth Vador's saber ?"
    

## Installation

Just copy and paste it, I won't judge you.
