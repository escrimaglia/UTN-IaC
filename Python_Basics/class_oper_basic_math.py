# Clase con funciones matematicas básicas
#
# ATENCION: los metodos de abajo estan definidos SIN `self`, a proposito.
# Llamarlos sobre una instancia lanza TypeError. Es el ejercicio del capitulo 4
# §4.6 del libro: reconocer el error, entender por que el mensaje habla de la
# cantidad de argumentos, y elegir entre los tres arreglos posibles.

class Basicas():
    def suma(a: int, b: int) -> int:
        """
        Suma dos números.

        Args:
            a (int): Primer número.
            b (int): Segundo número.

        Returns:
            int: La suma de a y b.
        """
        return a + b

    def resta(a: int, b: int) -> int:
        """
        Resta dos números.
        Args:
            a (int): Primer número.
            b (int): Segundo número.

        Returns:
            int: La resta de a y b.
        """
        return a - b
