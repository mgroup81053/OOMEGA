from settings import UnsupportedOperandTypeError, naive
from dataclasses import dataclass
from math import log
from function import *



primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997,]
def factorize(n: Constant):
    # n = prod(p in Prime) (p**k_p)
    if not (isinstance(n, Constant) and isinstance(n.value, int)):
        return ((n, 1),)
    
    n = n.value

    for p in (prime for prime in primes if prime**2 <= n):
        k_p = 0
        while True:
            if n % p == 0:
                n //= p
                k_p += 1
            else:
                break

        if k_p:
            yield (Constant(p), Constant(k_p))

    if n != 1:
        yield (Constant(n), Constant(1))

@naive
class FloatReal:
    def __init__(self, body):
        if isinstance(body, int):
            self.body = float(body)
        elif isinstance(body, float):
            self.body = body
        else:
            return TypeError(f"expected 'float' but found '{type(body).__name__}'")

    def __repr__(self):
        return str(self.body)

    def __pos__(self):
        return FloatReal(self.body)

    def __neg__(self):
        return FloatReal(-self.body)

    def __abs__(self):
        return FloatReal(abs(self.body))

    def __add__(self, other):
        if isinstance(other, FloatReal):
            return FloatReal(self.body + other.body)
        else:
            UnsupportedOperandTypeError(self, other, "+")

    def __mul__(self, other):
        if isinstance(other, FloatReal):
            return FloatReal(self.body * other.body)
        else:
            UnsupportedOperandTypeError(self, other, "*")

@dataclass
class NaiveLog:
    base: float
    antilogarithm: float

    def __mul__(self, other):
        if self.antilogarithm == other.base:
            return NaiveLog(self.base, other.antilogarithm)
        elif self.base == other.antilogarithm:
            return NaiveLog(self.antilogarithm, other.base)
        
    def __repr__(self):
        return str(log(self.antilogarithm, self.base))

class NaiveSqrt(Node):
    def __new__(cls, radix: Node):
        coef = Constant(1)

        for p, k_p in factorize(radix):
            if k_p >= Constant(2):
                coef *= Constant(p)**(Constant(k_p)//Constant(2))
                radix //= Constant(p)**((Constant(k_p)//Constant(2))*Constant(2))

        instance = super().__new__(cls)
        instance.radix = radix
        instance.children = []

        if radix == Constant(1):
            return coef
        elif coef == Constant(1):
            return instance
        else:
            return Operation(operating_func = mul, children=[coef, instance])
        
    def __init__(self, radix):
        self.radix = self.radix
        self.children = []

    def __repr__(self):
        return str(f"√({self.radix})")

    def __hash__(self):
        return hash(self.radix)
     
    def __eq__(self, other):
        if isinstance(other, NaiveSqrt):
            return self.radix == other.radix
        elif isinstance(other, Constant):
            return self.radix == other**Constant(2)

    def __mul__(self, other):
        if isinstance(other, NaiveSqrt):
            return NaiveSqrt(self.radix * other.radix)
        
    def __pow__(self, other):
        if other == 2:
            return self.radix

    @classmethod
    def rearrange(cls, instance, children, operating_func):
        if operating_func == mul:
            # sqrt(3) * sqrt(3) = 3
            targetChildren = set((child, frequency) for child in children if isinstance(child, Constant) and isinstance(child.value, NaiveSqrt) and (frequency:=children.count(child) >= 2))
            if targetChildren:
                new_children = children[:]
                for targetChild, frequency in targetChildren:
                    last_encounter = frequency - frequency%2
                    encounter = 0
                    for i, child in enumerate(children):
                        if child == targetChild:
                            encounter += 1
                            if encounter % 2:
                                new_children[i] = Constant(targetChild.value.radix)
                            else:
                                new_children[i] = Constant(1)

                            if encounter == last_encounter:
                                break

                    new_children = [child for child in new_children if child != Constant(1)]

                return Operation(mul, new_children)
        elif operating_func == add:
            # 5 + 4*sqrt(3)*sqrt(2) + 2*sqrt(3)*sqrt(2) = 5 + (4+2)*sqrt(3)*sqrt(2)
            leaves = instance.get_leaves()
            sqrt_leaves = [leaf for leaf in leaves if isinstance(leaf, NaiveSqrt)]
            target_leaves = {leaf for leaf in sqrt_leaves if sqrt_leaves.count(leaf) >= 2}

            for i, child_i in enumerate(children):
                if isinstance(child_i, Operation) and child_i.operating_func == mul and set(child_i.children).intersection(target_leaves):
                    for j, child_j in enumerate(children):
                        if i!=j and \
                            (isinstance(child_j, Operation) and child_j.operating_func == mul and set(child_i.children).intersection(set(child_j.children)).intersection(target_leaves) # ((3*sqrt(3)) + (4 * sqrt(3))
                             or isinstance(child_i, Operation) and child_j.operating_func == neg and child_j.children[0] in set(child_i.children).intersection(target_leaves) # sqrt(3) + -sqrt(3)
                             or child_j in set(child_i.children).intersection(target_leaves) # 3*sqrt(3) + sqrt(3)
                             ):

                            common_leaves = set(child_i.children).intersection(set(child_j.children)).intersection(target_leaves)
                            return Operation(add, 
                                             children[:i]+children[i+1:j]+children[j+1:]
                                             +[Operation(mul, [
                                                             Operation(add, 
                                                                        [Operation(mul, [c_i for c_i in child_i.children if c_i not in common_leaves]),
                                                                        Operation(mul, [c_j for c_j in child_j.children if c_j not in common_leaves])]),
                                                        *common_leaves
                                                        ])])


        return instance


    
@dataclass
class NaivePow(Node):
    def __new__(cls, base: Node, exponent: Node):
        if exponent == Constant(1):
            return base

        if all(isinstance(obj, Constant) and isinstance(obj.value, int) and obj.value >= 0 for obj in (base, exponent)):
            return Constant(base.value ** exponent.value)
        
        try:
            length = 0

            factors = factorize(base)
            next(factors)
            length = 1

            next(factors)
            length = 2
        except:
            pass

        instance = super().__new__(cls)
        if length == 0:
            instance = super().__new__(cls)

            instance.base = base
            instance.exponent = exponent
            instance.children = []

            return instance
        elif length == 1:
            (p, k_p), *_ = factorize(base)
            instance = super().__new__(cls)

            instance.base = p
            instance.exponent = k_p * exponent
            instance.children = []

            return instance
        else:
            return Operation(mul,
                             children=[NaivePow(p, Operation(mul, [Constant(k_p), exponent]))
                                       for p, k_p in factorize(base)])
        
    def __init__(self, base: Node, exponent: Node):
        self.base = self.base
        self.exponent = self.exponent
        self.children = []

    def __repr__(self):
        return f"{self.base}^{self.exponent}"


    # def __mul__(self, other):
    #     if isinstance(other, NaivePow) and self.base == other.base:
    #         return NaivePow(self.base, self.exponent + other.exponent)

    @classmethod
    def rearrange(cls, instance, children, operating_func):
        if operating_func == mul:
            powChildren = [child for child in children if isinstance(child, NaivePow)]

            if len(powChildren) >= 2:
                for i, child_i in enumerate(children):
                    if child_i in powChildren:
                        for j, child_j in enumerate(children):
                            if i != j and child_j in powChildren and child_i.base == child_j.base:
                                base = child_i.base
                                return Operation(mul, children[:i]+children[i+1:j]+children[j+1:]+
                                                 [NaivePow(base, child_i.exponent + child_j.exponent)])
                
        return instance
