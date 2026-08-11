# Script principal que utiliza (importa) las clases y scripts
#
# ATENCION: este script NO CORRE, y es a proposito. Tiene dos errores
# encadenados, y los dos son material del capitulo 4 del libro:
#
#   1. Falla en la linea de `basic.suma(5, 5)` con
#      TypeError: Basicas.suma() takes 2 positional arguments but 3 were given
#      Los metodos de Basicas y Advance estan definidos SIN `self`, asi que el
#      primer argumento se lo come la instancia. Ver el capitulo 4 §4.6, que
#      explica el error y sus tres arreglos posibles.
#
#   2. Si se arregla el primero, aparece el segundo:
#      AttributeError, porque `basic.multiplica()` y `basic.divide()` no existen
#      en la clase Basicas. Solo estan como funciones en script_basic.py, que es
#      de donde se importan arriba.
#
# El ejercicio consiste en arreglar los dos, en ese orden.

from class_oper_basic_math import Basicas
from class_oper_advance_math import Advance
from class_basic_attr import BasicMathAttr
from script_basic import multiplica, divide

if __name__ == "__main__":
    basic = Basicas()
    advance = Advance()
    basic_math = BasicMathAttr(10, 5)
    print ("Suma: ", basic.suma(5, 5))
    print ("Resta: ", basic.resta(5, 5))
    print ("Multiplica: ", basic.multiplica(5, 5))
    print ("Divide: ", basic.divide(5, 5))
    print ("Potencia: ", advance.potencia(5, 2))
    print ("Raíz Cuadrada: ", advance.raiz_cuadrada(25))
    print ("Clase Suma: ", basic_math.add())
    print ("Clase Resta: ", basic_math.subtract())
    print ("Script Multiplica: ", multiplica(10, 5))
    print ("Script Divide: ", divide(10, 5))