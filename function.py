from __future__ import annotations
from typing import Any, Callable, TypeVar
from dataclasses import dataclass, field
from functools import reduce

@dataclass
class NaiveRealFunction:
    root: Node

    def __call__(self, **vars):
        return self.root.evaluate(**vars)

class NaivePolynomial(NaiveRealFunction):
    def __init__(self, var: Variable, c_i: list):
        self.c_i = c_i
        while c_i[0] != 0 and c_i[-1] == 0:
            del c_i[-1]

        if not self.c_i:
            raise ValueError

        self.root = Operation(operating_func=add)

        for k, c_k in enumerate(c_i):
            var_to_the_k = Operation(
                operating_func=pow,
                children=[var, Constant(k)]
                )
            
            k_th_term = Operation(
                operating_func=mul,
                children=[Constant(c_k), var_to_the_k]
                )
            
            self.root.children.append(k_th_term)

    def __eq__(self, const):
        if len(self.c_i) == 2:
            return -self.c_i[0]/self.c_i[1]
        elif len(self.c_i) == 3:
            return [(-self.c_i[1]+(self.c_i[1]**2-4*self.c_i[2]*self.c_i[0])**(1/2))/(2*self.c_i[2]), (-self.c_i[1]-(self.c_i[1]**2-4*self.c_i[2]*self.c_i[0])**(1/2))/(2*self.c_i[2])]


class Node:
    def __init__(self, children: list[Node] = []):
        self.children = children

    def get_leaves(self):
        if self.children:
            return sum([child.get_leaves() for child in self.children], [])
        else:
            return [self]
        
    def __call__(self, **vars):
        return self.evaluate(**vars)

    def evaluate(self, **vars):
        if isinstance(self, Variable):
            try:
                return Constant(vars[self.var_name])
            except:
                return self
        elif isinstance(self, Operation):
            return self.operate(**vars)
        elif isinstance(self, Constant):
            return self
        else:
            raise TypeError
        
    def __neg__(self):
        return Operation(neg, [self])

    def __add__(self, other):
        if isinstance(other, Node):
            return Operation(add, [self, other])

    def __sub__(self, other):
        if isinstance(other, Node):
            return Operation(add, [self, -other])

    def __mul__(self, other):
        if isinstance(other, Node):
            return Operation(mul, [self, other])

    def __pow__(self, other):
        if isinstance(other, Node):
            return Operation(pow, [self, other])



class Variable(Node):
    def __init__(self, var_name: str):
        self.var_name = var_name
        self.children = []

    def __hash__(self):
        return hash(self.var_name)

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.var_name == other.var_name
        else:
            raise TypeError



class Constant(Node):
    def __new__(cls, value):
        if isinstance(value, Constant):
            return value
        else:
            instance = object.__new__(Constant)
            instance.value = value
            instance.children = []

            return instance
        
    def __init__(self, value):
        self.value = self.value
        self.children = []

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self):
        return str(self.value)
        # return f"Constant({self.value})"

    def __neg__(self):
        return Constant(-self.value)

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value

    def __le__(self, other):
        if isinstance(other, Constant):
            return self.value <= other.value
        
    def __floordiv__(self, other): #FIXME
        return Constant(self.value // other.value)

    @classmethod
    def rearrange(cls, instance, children, operating_func):
        constChildrenValue = [child.value for child in children if isinstance(child, Constant)]
        
        if operating_func == add:
            # 1 + 2 = 3
            if len(constChildrenValue) >= 2:
                summation = reduce(lambda a, b: a+b, constChildrenValue)

                children = [Constant(summation)] + [child for child in children if not isinstance(child, Constant)]
                return Operation(add, children)
        elif operating_func == mul:
            # 2 × 3 = 6
            if len(constChildrenValue) >= 2:
                product = reduce(lambda a, b: a*b, constChildrenValue)

                children = [Constant(product)] + [child for child in children if not isinstance(child, Constant)]
                return Operation(mul, children)

            # 2 × -f(x) = -2 × f(x)
            new_children = children[:]
            for i, child_i in enumerate(children):
                if isinstance(child_i, Operation) and child_i.operating_func == neg:
                    for j, child_j in enumerate(children):
                        if isinstance(child_j, Constant):
                            new_children[i] = child_i.children[0]
                            new_children[j] = -child_j

                            return Operation(mul, new_children)

            # 0 × f(x) = 0
            if Constant(0) in children:
                return Constant(0)

            # 1 × f(x) = f(x)
            if Constant(1) in children:
                i = children.index(Constant(1))
                return Operation(mul, children[:i] + children[i+1:])

            # -1 × f(x) = f(x)
            if Constant(-1) in children:
                i = children.index(Constant(-1))
                return -Operation(mul, children[:i] + children[i+1:])
        elif operating_func == pow:
            # 2 ^ 3 = 8
            if len(constChildrenValue) >= 2:
                hyperproduct = reduce(lambda a, b: a**b, constChildrenValue)

                children = [Constant(hyperproduct)] + [child for child in children if not isinstance(child, Constant)]
                return Operation(mul, children)

            # (f(x) ^ 0) ^ g(x) = 1
            if Constant(0) in children[1:]:
                i = children.index(Constant(0))
                return Constant(1)
        elif operating_func == neg:
            # -(1) = -1
            if isinstance(children[0], Constant):
                return -children[0]


        return instance
        

def neg(): ...
def add(): ...
def mul(): ...
def pow(): ...
class Operation(Node):
    def empty(self, children, **vars):
        raise ValueError

    TOperation = TypeVar("TOperation", bound="Operation")

    def __new__(cls, operating_func: Callable[[TOperation, list[Node], dict[str, Any]]] = empty, children=[]):
        instance = object.__new__(Operation)

        instance.children = children
        instance.operating_func = operating_func

        return Operation.rearrange(instance, children, operating_func)

    def __init__(self, operating_func: Callable[[TOperation, list[Node], dict[str, Any]]] = empty, children=[]):
        self.operating_func = self.operating_func
        self.children = self.children

    def __call__(self, **vars):
        return self.operate(**vars)
    
    def __hash__(self):
        return hash((self.operating_func, tuple(self.children)))
    
    def __repr__(self):
        if self.operating_func == add:
            return "+".join(repr(child) for child in self.children)
        elif self.operating_func == mul:
            return "".join(repr(child) for child in self.children)
        elif self.operating_func == neg:
            return f"-{self.children[0]}"

    @classmethod
    def rearrange(cls, instance, children, operating_func):
        if operating_func == neg and isinstance((child:=children[0]), Operation) and child.operating_func == neg:
            # -(-a) = a
            return child.children[0]

        if operating_func == add:
            # a + (-a) = 0
            isChanged = False
            for i, child in enumerate(children):
                if Operation(neg, [child]) in children:
                    children[i] = Constant(0)
                    children[children.index(Operation(neg, [child]))] = Constant(0)

                    isChanged = True

            children = [child for child in children if child != Constant(0)]

            if isChanged:
                return Operation(add, children)

            # (a + b) + c = a + b + c

            for i, child in enumerate(children):
                if isinstance(child, Operation) and child.operating_func == add:
                    return Operation(add, children[:i] + child.children + children[i+1:])

            # empty summation
            if len(children) == 0:
                return Constant(0)

        if operating_func == mul:
            # empty multiplication
            if len(children) == 0:
                return Constant(1)

            # a(b+c) = ab + ac
            for i, child in enumerate(children):
                if isinstance(child, Operation) and child.operating_func == add:
                    multiplier = children[:i]+children[i+1:]
                    multiplicands = child.children

                    return Operation(add, [Operation(mul, [*multiplier, multiplicand]) for multiplicand in multiplicands])

            # -a × -b = ab
            condition = lambda child: isinstance(child, Operation) and child.operating_func == neg
            frequency = sum(1 for child in children if condition(child))
            if frequency >= 2:
                last_encounter = frequency - frequency%2
                encounter = 0
                new_children = children[:]
                for i, child in enumerate(children):
                    if condition(child):
                        encounter += 1
                        new_children[i] = children[i].children[0]

                        if encounter == last_encounter:
                            break




                return Operation(mul, new_children)

            # (a × b) × c = a × b × c

            for i, child in enumerate(children):
                if isinstance(child, Operation) and child.operating_func == mul:
                    return Operation(mul, children[:i] + child.children + children[i+1:])

        if operating_func in (add, mul):
            # sole operation
            if len(children) == 1:
                return children[0]

        for base_type in Operation.base_type(instance):
            if hasattr(base_type, "rearrange"):
                returned = base_type.rearrange(instance, children, operating_func)
                if instance is not returned:
                    return returned

        return instance

    @classmethod
    def base_type(cls, node: Node):
        if not isinstance(node, Operation):
            return [type(node)]
        else:
            return sum([Operation.base_type(child) for child in node.children], [])

    def operate(self, **vars):
        return self
        # return self.operating_func(self.children, **vars)

    def __eq__(self, other):
        if isinstance(other, Operation):
            if self.operating_func == other.operating_func and self.children == other.children:
                return True

    def __add__(self, other):
        if self.operating_func == add:
            return Operation(add, self.children + other.children)
        
        return Operation(add, [self, other])

    def __mul__(self, other):
        if self.operating_func == mul:
            if isinstance(other, Operation):
                return Operation(mul, self.children + other.children)
            else:
                return Operation(mul, self.children + [other])

