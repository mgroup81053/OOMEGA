import inspect
from settings import Real_name, Matrix_name, Vector_name
from function import *
from number import *
from geometry import *

# https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
def my_import(name: str):
    components = name.split(".")
    module = __import__(components[0])
    subpart = ".".join(components[1:])

    # https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    for name, obj in inspect.getmembers(module):
        if name == subpart:
            return obj

# Real = my_import(f"number.{Real_name}")
Real = float
Matrix = my_import(f"matrix.{Matrix_name}")
Vector = my_import(f"matrix.{Vector_name}")




        