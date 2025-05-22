import operator


class Alias:
    def __init__(self, attribute_path: str):
        self.names = attribute_path.split(".")

    def __get__(self, owner, objtype=None):
        if owner is None:
            return self
        obj = owner
        for name in self.names:
            obj = getattr(obj, name)
        return obj

    def __set__(self, owner, value):
        obj = owner
        for name in self.names[:-1]:
            obj = getattr(obj, name)
        setattr(obj, self.names[-1], value)

    def __delete__(self, owner):
        delattr(obj, self.attribut_name)


class OperableProperty:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = "_" + name
        self.__doc__ = f"OperableProperty '{name}' of {owner!r}."

    def __get__(self, owner, ownertype=None):
        if owner is None:
            # Necessesary to reference an instance at class creation,
            # when it does not have an owner yet.
            return self
        return getattr(owner, self.private_name)

    def __set__(self, owner, val):
        setattr(owner, self.private_name, val)

    def __mul__(self, other):
        return Result(operator.mul, self, other)

    def __rmul__(self, other):
        return Result(operator.mul, other, self)

    def __truediv__(self, other):
        return Result(operator.truediv, self, other)

    def __rtruediv__(self, other):
        return Result(operator.truediv, other, self)

    def __add__(self, other):
        return Result(operator.add, self, other)

    def __radd__(self, other):
        return Result(operator.add, other, self)

    def __sub__(self, other):
        return Result(operator.sub, self, other)

    def __rsub__(self, other):
        return Result(operator.sub, other, self)

    # ...More operations could be defined, but I am lazy



class Result(OperableProperty):
    def __init__(self, operation, *values):
        self.operation = operation
        self.values = values

    def __get__(self, owner, ownertype=None):
        if owner is None:
            return self
        values = []
        for v in self.values:
            if isinstance(v, OperableProperty):
                values.append(v.__get__(owner))
            elif isinstance(v, str) and v.startswith('@'):
                values.append(getattr(owner, v[1:]))
            else:
                values.append(v)
        return self.operation(*values)

    def __set__(self, owner, value):
        raise AttributeError(
            f"{self.name} is the result of an operation and is not writable"
        )
