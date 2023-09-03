from __future__ import annotations
from functools import reduce
import matplotlib.pyplot as plt

class Function:
    @staticmethod
    def __defalt_getVarValue(self, *arg, **kwarg):
        # getVarValue by ImplicitVarTable
        if len(arg) == len(self.implicitVarTable):
            for var, varValue in zip(self.implicitVarTable, arg):
                kwarg[var.varName] = varValue

        for varName, varValue in kwarg.items():
            if varName is self.varName:
                return varValue

    @staticmethod
    def __getVarValue_SchemeForUnaryOperation(self, binaryOperation, baseVar, baseVarName, *arg, **kwarg):
        # getVarValue by ImplicitVarTable
        if len(arg) == len(self.implicitVarTable):
            for var, varValue in zip(self.implicitVarTable, arg):
                kwarg[var.varName] = varValue

        for varName, varValue in kwarg.items():
            if varName is baseVarName:
                return binaryOperation(baseVar(varValue))

    @staticmethod
    def __getVarValueGetter_SchemeForUnaryOperation(binaryOperation, baseVar, baseVarName):
        return lambda self, *arg, **kwarg: Function.__getVarValue_SchemeForUnaryOperation(self, binaryOperation, baseVar, baseVarName, *arg, **kwarg)

    @staticmethod
    def __getVarValue_SchemeForBinaryOperation(self, binaryOperation, baseVar, baseVarName, other, *arg, **kwarg):
        # getVarValue by ImplicitVarTable
        if len(arg) == len(self.implicitVarTable):
            for var, varValue in zip(self.implicitVarTable, arg):
                kwarg[var.varName] = varValue

        for varName, varValue in kwarg.items():
            if varName is baseVarName:
                try:
                    return binaryOperation(baseVar(varValue), other(varValue))
                except:
                    return binaryOperation(baseVar(varValue), other)

    @staticmethod
    def __getVarValueGetter_SchemeForBinaryOperation(binaryOperation, baseVar, baseVarName, other):
        return lambda self, *arg, **kwarg: Function.__getVarValue_SchemeForBinaryOperation(self, binaryOperation, baseVar, baseVarName, other, *arg, **kwarg)

    def __init__(self, varName=None, varRange=None, varValueGetter = __defalt_getVarValue, implicitVarTable = []):
        self.varName = varName # The name of the Variable. Don't be confused with the variable name in python.
        self.varRange = varRange # The range of the Variable. Used to plotting.
        self.varValueGetter = varValueGetter # The method used to get the value of the Variable, given inputs; `varValueGetter(self.varName, *arg, **kwarg)`

        self.implicitVarTable = implicitVarTable # Used when there are implicit assignment; e.g. `subtraction.implicitVarTable = [x, y]; subtraction(1, 2) -> -1; subtraction(x=1, y=2) -> -1`
        if varName is not None:
            self.implicitVarTable.append(self)

    def plot(self):
        """Works properly if the Function has 1 free variable."""
        plt.plot(self.varRange, self(self.varRange))

    def __repr__(self):
        self.plot()
        plt.show()
        return ""

    def __call__(self, *arg, **kwarg):
        return self.varValueGetter(self, *arg, **kwarg)

    def __pos__(self):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForUnaryOperation(lambda a: +a, self, self.varName), implicitVarTable=[self])

    def __neg__(self):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForUnaryOperation(lambda a: -a, self, self.varName), implicitVarTable=[self])

    def __abs__(self):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForUnaryOperation(lambda a: abs(a), self, self.varName), implicitVarTable=[self])

    def __add__(self, other):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForBinaryOperation(lambda a, b: a+b, self, self.varName, other), implicitVarTable=[self])

    def __radd__(self, other) -> Function:
        return self + other

    def __sub__(self, other):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForBinaryOperation(lambda a, b: a-b, self, self.varName, other), implicitVarTable=[self])

    def __rsub__(self, other) -> Function:
        return self - other

    def __mul__(self, other):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForBinaryOperation(lambda a, b: a*b, self, self.varName, other), implicitVarTable=[self])

    def __rmul__(self, other) -> Function:
        return self * other

    def __truediv__(self, other):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForBinaryOperation(lambda a, b: a/b, self, self.varName, other), implicitVarTable=[self])

    def __rtruediv__(self, other) -> Function:
        return self / other

    def __pow__(self, other):
        return Function(varName=None, varRange=self.varRange, varValueGetter=Function.__getVarValueGetter_SchemeForBinaryOperation(lambda a, b: a**b, self, self.varName, other), implicitVarTable=[self])
    
class Variable(Function):
    pass

class Matrix:
    @staticmethod
    def identity(size):
        ROW = 0; COL = 1
        return Matrix([[(0 if i != j else 1) for j in range(size[COL])] for i in range(size[ROW])])

    def __init__(self, elements):
        # 2d matrices only

        self.elements = elements # [row1, row2, ...]
        self.size = (len(elements), len(elements[0])) # (row, col)

        ROW = 0; COL = 1
        self.rows = [[elements[i][j] for j in range(self.size[COL])] for i in range(self.size[ROW])]
        self.cols = [[elements[i][j] for i in range(self.size[ROW])] for j in range(self.size[COL])]

    def __pos__(self):
        return Matrix([[+elem for elem in row] for row in self.rows])

    def __neg__(self):
        return Matrix([[-elem for elem in row] for row in self.rows])

    def __add__(self, other):
        return Matrix([[self_elem + other_elem for self_elem, other_elem in zip(self_row, other_row)] for self_row, other_row in zip(self.rows, other.rows)])

    def __sub__(self, other):
        return Matrix([[self_elem - other_elem for self_elem, other_elem in zip(self_row, other_row)] for self_row, other_row in zip(self.rows, other.rows)])

    def __mul__(self, other):
        try:
            ROW = 0; COL = 1
            return Matrix([[sum(a*b for a, b in zip(self.rows[i], other.cols[j])) for j in range(other.size[COL])] for i in range(self.size[ROW])])
        except:
            return Matrix([[other * elem for elem in row] for row in self.rows])

    def __rmul__(self, other):
        return self * other
    
    def __pow__(self, other):
        if isinstance(other, int) and other >= 0:
            I = Matrix.identity(self.size)

            return reduce(lambda a, b: a*b, [self]*other, I)
        else:
            raise

    def __repr__(self):
        return repr(self.rows)
