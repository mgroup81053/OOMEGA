from __future__ import annotations
from typing import Any, Callable, TypeVar
from dataclasses import dataclass

@dataclass
class NaiveRealFunction:
    root: Node

    def __call__(self, **vars):
        return self.root.evaluate(**vars)

class NaivePolynomial(NaiveRealFunction):
    def __init__(self, var: Variable, c_i: list):
        temp_root = Operation(operating_func=Operation.add, left_child=Constant(value=0))
        last_parent = temp_root

        for k, c_k in enumerate(c_i):
            var_to_the_k = Operation(
                operating_func=Operation.pow,
                left_child=var,
                right_child=Constant(value=k)
                )
            
            k_th_term = Operation(
                operating_func=Operation.mul,
                left_child=Constant(value=c_k),
                right_child=var_to_the_k
                )
            
            last_parent.right_child = Operation(operating_func=Operation.add, left_child=k_th_term)
            last_parent = last_parent.right_child

        last_parent.right_child = Constant(value=0)
        self.root = temp_root.right_child


@dataclass
class Node:
    left_child: Node | None = None
    right_child: Node | None = None

    def for_all_descendants(self, func):
        for child in (self.left_child, self.right_child):
            if child == None:
                continue

            child.for_all_descendants(func)

            return func(child)

    def evaluate(self, **vars):
        if isinstance(self, Variable):
            try:
                return vars[self.var_name]
            except:
                return self
        elif isinstance(self, Operation):
            return self.operate(**vars)
        elif isinstance(self, Constant):
            return self.value
        else:
            raise TypeError



@dataclass(kw_only=True)
class Variable(Node):
    var_name: str

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.var_name == other.var_name
        else:
            raise TypeError



@dataclass(kw_only=True)
class Constant(Node):
    value: Any | None = None

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            raise TypeError
        

@dataclass()
class Operation(Node):
    def empty(self, left_child, right_child, **vars):
        raise ValueError

    TOperation = TypeVar("TOperation", bound="Operation")
    operating_func: Callable[[TOperation, Node|None, Node|None, dict[str, Any]]] = empty

    def add(left_child, right_child, **vars):
        if isinstance(left_child, Node) and isinstance(right_child, Node):
            return left_child.evaluate(**vars) + right_child.evaluate(**vars)
        else:
            raise ValueError

    def mul(left_child, right_child, **vars):
        if isinstance(left_child, Node) and isinstance(right_child, Node):
            return left_child.evaluate(**vars) * right_child.evaluate(**vars)
        else:
            raise ValueError

    def pow(left_child, right_child, **vars):
        if isinstance(left_child, Node) and isinstance(right_child, Node):
            return left_child.evaluate(**vars) ** right_child.evaluate(**vars)
        else:
            raise ValueError

    def operate(self, **vars):
        return self.operating_func(self.left_child, self.right_child, **vars)

