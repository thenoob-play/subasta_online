from sqlalchemy.orm import Session
from sqlalchemy import text
from DataBase.connection import get_db

def crear_registro_usuario(data):
    db: Session = next(get_db())
    try:
        # Corregido: la tabla se llama 'usuario' en singular según tu Workbench
        query = text("""
            INSERT INTO usuario (nombre, correo, password, telefono, rol, activo, fecha_registro) 
            VALUES (:nombre, :correo, :password, :telefono, :rol, :activo, :fecha_registro)
        """)
        
        if "fecha_registro" in data and data["fecha_registro"]:
            if hasattr(data["fecha_registro"], "strftime"):
                data["fecha_registro"] = data["fecha_registro"].strftime('%Y-%m-%d %H:%M:%S')

        db.execute(query, data)
        db.commit()
        return True
    except Exception as err:
        print(f"❌ Error detallado en la base de datos: {err}")
        db.rollback()
        return False
    
    
def crear_registro_vendedor(data):
    db: Session = next(get_db())
    try:
        # 1. Insertar primero los datos generales en la tabla 'usuario'
        query_usuario = text("""
            INSERT INTO usuario (nombre, correo, password, telefono, rol, activo, fecha_registro) 
            VALUES (:nombre, :correo, :password, :telefono, :rol, :activo, :fecha_registro)
        """)
        
        if "fecha_registro" in data and data["fecha_registro"]:
            if hasattr(data["fecha_registro"], "strftime"):
                data["fecha_registro"] = data["fecha_registro"].strftime('%Y-%m-%d %H:%M:%S')

        # Ejecutamos la inserción del usuario
        resultado = db.execute(query_usuario, data)
        
        # Obtenemos el ID autoincrementable que se acaba de crear en 'usuario'
        id_usuario = resultado.lastrowid

        # 2. Insertar los datos específicos en la tabla 'vendedor' usando el id_usuario
        query_vendedor = text("""
            INSERT INTO vendedor (id_usuario, documento, nombre_comercial, direccion, cuenta_bancaria) 
            VALUES (:id_usuario, :documento, :nombre_comercial, :direccion, :cuenta_bancaria)
        """)
        
        # Preparamos el diccionario con los campos requeridos por la tabla 'vendedor'
        data_vendedor = {
            "id_usuario": id_usuario,
            "documento": data.get("documento"),
            "nombre_comercial": data.get("nombre_comercial"),
            "direccion": data.get("direccion"),
            "cuenta_bancaria": data.get("cuenta_bancaria")
        }

        db.execute(query_vendedor, data_vendedor)
        
        # Confirmamos ambos cambios en la base de datos
        db.commit()
        return True
        
    except Exception as err:
        print(f"❌ Error detallado en la base de datos: {err}")
        db.rollback()
        return False
    
#login del usuario ( obtener contraseña )
def obtener_contrasena_por_correo(correo: str):
    db: Session = next(get_db())
    try:
        query = text("""
            SELECT password FROM usuario WHERE correo = :correo;
        """)
        result = db.execute(query, {"correo": correo}).fetchone()
        if result is not None:
            print(f"en crud AQUII {result}")
            # Retornamos el valor de la contraseña (puede ser result[0] o result.contrasena dependiendo de tu ORM/driver)
            return result
         
        else:
            return None
    except Exception as err:
        print(f"❌ Error detallado en la base de datos: {err}")
        db.rollback()
        return None


def obtener_rol_por_correo(correo: str):
    db: Session = next(get_db())
    try:
        query = text("SELECT rol FROM usuario WHERE correo = :correo")
        return db.execute(query, {"correo": correo}).scalar_one_or_none()
    except Exception as err:
        print(f"❌ Error al obtener el rol del usuario: {err}")
        db.rollback()
        return None


def verificar_correo_telefono_existente(correo, telefono):
    db: Session = next(get_db())
    try:
        query = text("""
            SELECT * FROM usuario WHERE correo = :correo OR telefono = :telefono
        """)
        result = db.execute(query, {"correo": correo, "telefono": telefono}).fetchone()
        return result is not None
    except Exception as err:
        print(f"❌ Error al verificar correo o teléfono: {err}")
        return False    
    

def validar_documento_cuentaBancaria(documento, cuenta_bancaria):
    db: Session = next(get_db())
    try:
        query = text("""
            SELECT 1
            FROM vendedor
            WHERE documento = :documento OR cuenta_bancaria = :cuenta_bancaria
            LIMIT 1
        """)
        result = db.execute(query, {"documento": documento, "cuenta_bancaria": cuenta_bancaria}).fetchone()
        return result is not None
    except Exception as err:
        print(f"❌ Error al verificar documento o cuenta bancaria: {err}")
        return False
    

def obtener_id_vendedor(correo):
    db: Session = next(get_db())
    try:
        query = text("SELECT id_usuario FROM usuario WHERE correo = :correo")
        result = db.execute(query, {"correo": correo}).fetchone()
        if result:
            return result[0]  # Devuelve el id_usuario
        else:
            return None  # No se encontró el usuario
    except Exception as err:
        print(f"❌ Error al obtener el id de usuario: {err}")
        return None
    

def obtener_datos_para_modificar(correo):
    db: Session = next(get_db())
    try:
        query = text("""
            SELECT password FROM usuario WHERE correo = :correo
        """)
        result = db.execute(query, {"correo": correo}).fetchone()
        return result[0] if result else None
    finally:
        db.close()


def modificar_usuarios(data, correo):
    campos_permitidos = {"nombre", "password", "telefono"}
    if len(data) != 1 or not set(data).issubset(campos_permitidos):
        raise ValueError("Debe modificarse exactamente un campo permitido")

    campo = next(iter(data))
    db: Session = next(get_db())
    try:
        query_usuario = text(f"""
            UPDATE usuario SET {campo} = :valor WHERE correo = :correo
        """)
        db.execute(query_usuario, {"valor": data[campo], "correo": correo})
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()