# For postponed evaluation of annotations
from __future__ import annotations 
from settings import UnsupportedOperandTypeError, naive, size, EmptyObj
from functools import reduce

Real = float

class PureMatrix:
    def __init__(self, rows: list[list[Real]]):
        # Type/Value check
        if not (isinstance(rows, list) and isinstance(rows[0], list)):
            raise TypeError("only 2d matrices are supported")
        else:
            row_len = len(rows[0])
            for row in rows:
                if len(row) != row_len:
                    raise ValueError(f"a matrix should have a rectangular size ({len(rows)}×{row_len}) but found a row with size of {len(row)}")
                for elem in row:
                    if not isinstance(elem, Real):
                        raise TypeError(f"element(s) should be 'Real' but found '{type(elem).__name__}'")

        self.rows = rows
        self.columns = [list(col_elems) for col_elems in zip(*rows)]

    @classmethod
    def size(cls, A: PureMatrix):
        return (Real(len(A.rows)), Real(len(A.columns)))

    @classmethod
    def LU(cls, A: PureMatrix):
        #FIXME
        return PureMatrix(), PureMatrix()

    @classmethod
    def det(cls, A):
        return abs(A)
    
    @classmethod
    def inverse(cls, A):
        return PureMatrix() #FIXME
    
    @classmethod
    def identity(cls, size):
        if not isinstance(size, list):
            raise TypeError(f"expected 'list' but found '{type(size).__name__}'")
        
        if len(size) != 2:
            raise TypeError("only 2d matrices are supported")
        
        if size[0] != size[1]:
            raise ValueError(f"a matrix should be a square but found ({size[0]}×{size[1]})")

        length = size[0]
        return PureMatrix([[(0 if i!=j else 1) for j in range(length)] for i in range(length)])

    def __repr__(self):
        return str(self.rows)

    def __abs__(A):
        row_len = PureMatrix.size(A)[0]
        col_len = PureMatrix.size(A)[1]

        if row_len != col_len:
            raise ValueError(f"only square matrices have determinants but found a {col_len}×{row_len} matrix")
        else:
            L, U = PureMatrix.LU(A)
            det_L = reduce(lambda x, y: x*y, (L.rows[i][i] for i in range(row_len)))
            det_U = reduce(lambda x, y: x*y, (U.rows[i][i] for i in range(row_len)))

            S = 0 #FIXME

            return Real(-1)**S * det_L * det_U

    def __mul__(A, B):
        if isinstance(B, PureMatrix):
            if PureMatrix.size(A)[1] == PureMatrix.size(B)[0]:
                return PureMatrix([[sum((row_elem*col_elem for row_elem, col_elem in zip(row, column)), Real(0.0)) for column in B.columns] for row in A.rows])
            else:
                raise ValueError(f"the first matrix's number of column ({PureMatrix.size(A)[1]}) should be equal to the second matrix's number of row ({PureMatrix.size(B)[0]})")
        else:
            raise UnsupportedOperandTypeError(A, B)
        
    def __pow__(A, n):
        if isinstance(n, Real): #FIXME: isinstance(n, Natural)
            mul = lambda M, N: M*N

            if n < Real(0):
                return reduce(mul, (PureMatrix.inverse(A),)*n)
            elif n == Real(0):
                return PureMatrix.identity(PureMatrix.size(A))
            else: # elif n > Real(0):
                return reduce(mul, (A,)*n)


class PureVector(PureMatrix):
    def __init__(self, column: list[Real]):
        # Type check
        if not (isinstance(column, list) and not isinstance(column[0], list)):
            raise TypeError("only 1d column vector is supported")
        else:
            for elem in column:
                if not isinstance(elem, Real):
                    raise TypeError(f"element(s) should be Real but found '{type(elem).__name__}'")

        self.columns = [column]
        self.rows = [[elem] for elem in column]
        self.elements = column

    def __repr__(self):
        return str(tuple(self.elements))

    def __rmul__(x, A):
        if isinstance(A, PureMatrix):
            if PureMatrix.size(A)[1] == PureMatrix.size(x)[0]:
                return PureVector([sum((row_elem*col_elem for row_elem, col_elem in zip(row, x.elements)), Real(0.0)) for row in A.rows])
            else:
                raise ValueError(f"the first matrix's number of column ({PureMatrix.size(x)[1]}) should be equal to the second matrix's number of row ({PureMatrix.size(A)[0]})")
        else:
            raise UnsupportedOperandTypeError(x, A)
        
    def inner_prod(u, v):
        return u.elements[0]*v.elements[0] + u.elements[1]*v.elements[1] #FIXME
    




@naive
class NaiveMatrix:
    def __init__(self, elements: list[list[float]]):
        self.body = EmptyObj()
        self.body.elements = elements

    def size(self):
        return (len(self.body.elements), len(self.body.elements[0]))

    def __repr__(self):
        return str(self.body.elements)

    def __add__(self, other):
        if isinstance(other, NaiveMatrix) and size(self) == size(other):
            return NaiveMatrix(
                [[selfElement + otherElement for selfElement, otherElement in zip(selfRow, otherRow)]
                    for selfRow, otherRow in zip(self.body.elements, other.body.elements)])


@naive
class NaiveVector(NaiveMatrix):
    def __init__(self, elements: list[float]):
        self.body = EmptyObj()
        self.body.elements = [[element] for element in elements]
        self.body.column = elements

    def __repr__(self):
        return str(self.body.column)
    
    def __add__(self, other):
        if isinstance(other, NaiveVector) and size(self) == size(other):
            return NaiveVector(
                [selfElement + otherElement for selfElement, otherElement
                  in zip(self.body.column, other.body.column)])



