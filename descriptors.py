from abc import ABC, abstractmethod

import operator

class _ExpressionDescriptor(ABC):
    """Abstract class for the descriptors defined in this module. This
    class is designed to be inherited. This class defines the
    __set_name__ dunder method, as well as any operator overload.
    """

    def __set_name__(self, owner, name):
        self.name = name
        self.__doc__ = (
            f"{self.__class__.__name__} '{name}' of "
            f"class '{owner.__name__}'."
        )

    @abstractmethod
    def __get__(self, owner, ownertype=None):
        return

    @abstractmethod
    def __set__(self, owner, val):
        pass

    @abstractmethod
    def __delete__(self, owner):
        pass

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

    # More operations could be defined...
    # ...but I'm lazy and I don't need them.

class OperableProperty(_ExpressionDescriptor):
    """A descriptor for an attribute of a class on which operations can
    be done. This attribute can be set or deleted if necessary.
    """
    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self.private_name = "_" + name

    def __get__(self, owner, ownertype=None):
        if owner is None:
            # Necessesary to reference an instance at class creation,
            # when it does not have an owner yet. This is what allows
            # the use of expressions.
            return self
        try:
            a = getattr(owner, self.private_name)
        except AttributeError as e:
            msg = str(e).replace(self.private_name, self.name)
            raise AttributeError(msg) from e
        return a

    def __set__(self, owner, val):
        setattr(owner, self.private_name, val)

    def __delete__(self, owner):
        delattr(owner, self.private_name)


class Result(_ExpressionDescriptor):
    """The result of an operation. This result can be used in other
    expressions.

    Args:
        operation (Callable) : function used to compute the result
                               at runtime, when requested.
        values (Any) : values to use as parameters for the operation
        kwargs : keyword arguments of operation, if applicable.
    """
    def __init__(self, operation, *values, **kwargs):
        self.operation = operation
        self.values = values
        self.kwargs = kwargs

    def __get__(self, owner, ownertype=None):
        if owner is None:
            return self
        values = [
            v.__get__(owner) if isinstance(v, _ExpressionDescriptor) else v
            for v in self.values
        ]
        return self.operation(*values, **self.kwargs)

    def __set__(self, owner, value):
        msg = f"{self.name} is the result of an operation and is not writable"
        raise AttributeError(msg)

    def __delete__(self, owner):
        msg = f"{self.name} is the result of an operation and is not deletable"
        raise AttributeError(msg)


class Alias(_ExpressionDescriptor):
    """"""
    def __init__(self, attribute_path: str):
        self.attribute_path = attribute_path
        self.names_list = attribute_path.split(".")
        self.attribute_name = self.names_list[-1]

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self.__doc__ = f"Alias of '{owner.__name__}.{self.attribute_path}'"

    def _get_last_object(self, owner):
        obj = owner
        for name in self.names_list[:-1]:
            obj = getattr(obj, name)
        return obj

    def __get__(self, owner, objtype=None):
        if owner is None:
            return self
        obj = self._get_last_object(owner)
        try:
            a = getattr(obj, self.attribute_name)
        except AttributeError as e:
            msg = str(e) + " (accessed from alias)"
            raise AttributeError(msg) from e
        return a

    def __set__(self, owner, value):
        obj = self._get_last_object(owner)
        setattr(obj, self.attribute_name, value)

    def __delete__(self, owner):
        obj = self._get_last_object(owner)
        delattr(obj, self.attribute_name)
