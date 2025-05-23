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

    'A' object has no attribute 'val' (accessed from alias)
    

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

shmi = FamilyMember('Shmi Skywalker')
anakin = FamilyMember('Anakin Skywalker', mother=shmi)
luke = FamilyMember('Luke Skywalker', father=anakin)

print(f"{luke.paternal_grandmother.name = }")
```

    luke.paternal_grandmother.name = 'Shmi Skywalker'
    

### ``OperableProperty``

The descriptor ``OperableProperty`` allows the creation of attributes and then to do operations on these attributes to declare properties of the class. These expressions are then only evaluated at runtime, thus taking into account any updates. 

This is already possible in Python using the ``@property`` decorator, but this descriptors makes these definitions more readable and less boilerplate for simple cases. In the following example, a similar behaviour is implemented twice, once using the ``@property`` decorator and once using ``OperableProperty``.

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
    

Here, these two examples are just as long, but in practical applications the second example is more easily readable, especially if the number of properties is high.

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
    
    age_timedelta = datetime.now() - date_of_birth
    # Most types that support common operators are fine

    age = Alias('age_timedelta.days') / 364.2425
    # Access to age_timedelta.days with an alias, and 
    # divide by 365.2425, which is the number of days in a year

    nickname = name + ' a.k.a. Darth Vader'
    # Reference to name, which is already defined by an expression

    
p = Person(
    first_name='Anakin', 
    last_name='Skywalker', 
    date_of_birth=datetime(year=1999, month=10, day=13)
)
print(f'{p.name = }')
print(f'{p.nickname = }')
print(f'{p.age = :.1f} years old')
```

    p.name = 'Anakin Skywalker'
    p.nickname = 'Anakin Skywalker a.k.a. Darth Vader'
    p.age = 25.7 years old
    

### Class inheritance and ``OperableProperty``

The behaviour of ``OperableProperty`` is slightly modified in case of class inheritance, since the instances are only available in the namespace they are declared in. In that case, an attribute can be accessed using ``Alias`` as follows:


```python
@dataclass
class LightSaber:
    owner: str = OperableProperty()

    # Access RedSaber.color using '@color'
    exclamation = owner + ' wields a ' + Alias('color') + ' lightsaber !'

class RedSaber(LightSaber):
    color = 'red'

    # Access LightSaber.owner by name
    interrogation = "Is That " + Alias('owner') + "'s saber ?"

vador_saber = RedSaber('Darth Vador')

print(f'{vador_saber.exclamation = }')
print(f'{vador_saber.interrogation = }')
```

    vador_saber.exclamation = 'Darth Vador wields a red lightsaber !'
    vador_saber.interrogation = "Is That Darth Vador's saber ?"
    

Note that in that case ``color`` is not an attribute of the ``Lightsaber`` class, thus trying to print ``exclamation`` raises an error:


```python
try:
    print(LightSaber('Obi Wan Kenobi').exclamation)
except AttributeError as e:
    print(e)
```

    'LightSaber' object has no attribute 'color' (accessed from alias)
    

### Advanced example using ``Result``

Some advanced applications are possible using the ``Result`` descriptor. This descriptor takes a ``Callable`` and any numer of argument and keyword arguments as an expression:


```python
from descriptors import Result
import math

@dataclass
class Angle:
    value_degree: float = OperableProperty()

    value_radian = Result(math.radians, value_degree)
    # Apply the function math.radians to Angle.value_degree

    value_radian_rounded = Result(
        lambda x: (lambda n : round(x, n)),
        value_radian,
    )
    # Create a method of Angle that rounds value_radian to the 
    # given number of digits

theta = Angle(45) # 45°

print(f"{theta.value_radian = } rad")
print(f"{theta.value_radian_rounded(2) = } rad (approximately)")
```

    theta.value_radian = 0.7853981633974483 rad
    theta.value_radian_rounded(2) = 0.79 rad (approximately)
    

## Ethical considerations

"They spent so much time wondering if they could, that they forgot to ask themself if they should"

So should you use this module ? Honestly, probably not. I'm pretty sure there are some cases where the behaviours of these descriptors would make things harder to read, particularly when using ``Result`` directly. Plus, there is always an edge case that breaks everything, but I haven't found it yet.

In addition, These descriptors kind of change the behaviour of Python in a way that an end user or another programmer might not forsee, which is an issue. Also, you probably shouldn't want to define aliases in your code for any other reason than backward compatibility, and even then it is probably better (more pythonic) to create a wrapper class.

Still, these descriptors work quite well for some simple applications and helped me make one of my projects more readable. As long as everyone is adult and consenting, I guess it's fine.

## Installation

Just copy and paste the descriptors.py file, I won't judge you.
