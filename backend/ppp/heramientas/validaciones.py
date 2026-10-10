
import bcrypt

def encriptar_password(password: str) -> str:
    """Toma una contraseña plana y devuelve su hash seguro."""
    # Convertimos la contraseña a bytes y generamos el hash con bcrypt
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verificar_password(password_plana: str, password_hash: str) -> bool:
    """Compara una contraseña escrita por el usuario con el hash guardado en la BD."""
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hash.encode('utf-8'))

# Validar correo si el correo no termina en @gmail.com o @hotmail.com devolver False
def validar_email(email):
    if email.endswith("@gmail.com") or email.endswith("@hotmail.com") or email.endswith("@outlook.com"):
        return True
    else:
        return False
    
    