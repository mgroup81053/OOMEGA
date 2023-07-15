from settings import UnsupportedOperandTypeError


class FloatReal:
    def __init__(self, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            return TypeError(f"expected 'float' but found '{type(value).__name__}'")
        else:
            self.value = value

    def __repr__(self):
        return str(self.value)

    def __pos__(self):
        return FloatReal(self.value)

    def __neg__(self):
        return FloatReal(-self.value)

    def __abs__(self):
        return FloatReal(abs(self.value))

    def __add__(self, other):
        if isinstance(other, FloatReal):
            return FloatReal(self.value + other.value)
        else:
            UnsupportedOperandTypeError(self, other)

    def __mul__(self, other):
        if isinstance(other, FloatReal):
            return FloatReal(self.value * other.value)
        else:
            UnsupportedOperandTypeError(self, other)



        