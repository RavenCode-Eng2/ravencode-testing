import random
import string

def generar_email_aleatorio():
    """Genera un email aleatorio para evitar conflictos en pruebas."""
    letras = string.ascii_lowercase
    nombre = ''.join(random.choice(letras) for _ in range(8))
    return f"{nombre}@test.com"

def generar_nombre_aleatorio():
    """Genera un nombre aleatorio para las pruebas."""
    nombres = ["Ana", "Carlos", "María", "Juan", "Sofía", "Luis", "Carmen", "Pedro"]
    apellidos = ["García", "López", "Martínez", "Rodríguez", "González", "Pérez", "Sánchez"]
    return f"{random.choice(nombres)} {random.choice(apellidos)}" 