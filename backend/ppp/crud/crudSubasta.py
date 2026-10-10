import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session
from sqlalchemy import text
from DataBase.connection import SessionLocal, get_db
from backend.ppp.validaciones import (
    comparar_montos,
    validar_monto,
    validar_programacion,
)


def _solicitar_json(url, datos=None, token=None):
    cuerpo = None if datos is None else json.dumps(datos).encode("utf-8")
    encabezados = {"Accept": "application/json"}
    if cuerpo is not None:
        encabezados["Content-Type"] = "application/json"
    if token:
        encabezados["Authorization"] = f"Bearer {token}"

    solicitud = Request(url, data=cuerpo, headers=encabezados)
    try:
        with urlopen(solicitud, timeout=10) as respuesta:
            resultado = json.loads(respuesta.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"El servicio {url} respondió HTTP {error.code}") from error
    except OSError as error:
        raise RuntimeError(f"No se pudo conectar con el servicio {url}") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"El servicio {url} no respondió con JSON válido") from error

    if not isinstance(resultado, dict) or resultado.get("status") != "success":
        raise RuntimeError(f"El servicio {url} devolvió una respuesta inválida")
    return resultado


def _obtener_ultima_puja(id_subasta):
    url_base = os.getenv("PUJA_API_URL", "http://localhost").rstrip("/")
    resultado = _solicitar_json(
        f"{url_base}/puja/ultima/{id_subasta}"
    )
    puja = resultado.get("data")
    if puja is not None and (
        not isinstance(puja, dict)
        or "monto" not in puja
        or "usuario_id_usuario" not in puja
    ):
        raise RuntimeError("La API PHP devolvió datos incompletos de la última puja")
    return puja


def _crear_pago_pendiente(id_subasta, monto, id_comprador):
    url = os.getenv(
        "PAGO_API_URL",
        "http://localhost:3000/api/pagos/subasta",
    )
    with SessionLocal() as db:
        correo = db.execute(
            text("""
                SELECT correo
                FROM usuario
                WHERE id_usuario = :id_comprador
                  AND rol = 'comprador'
                  AND activo = 1
            """),
            {"id_comprador": id_comprador},
        ).scalar_one_or_none()
    if correo is None:
        raise RuntimeError("No se encontró el correo del comprador activo")

    return _solicitar_json(
        url,
        {
            "subasta_id_subasta": id_subasta,
            "monto": str(monto),
            "correo": correo,
        },
    )


def crear_subasta_con_articulo(data, vendedor_correo):
    imagenes = data["imagen_url"]

    with SessionLocal.begin() as db:
        id_categoria = db.execute(
            text("SELECT id_categoria FROM categoria WHERE nombre = :categoria"),
            {"categoria": data["categoria"]},
        ).scalar_one_or_none()
        if id_categoria is None:
            raise LookupError("La categoría no existe")

        id_vendedor = db.execute(
            text("""
                SELECT id_usuario
                FROM usuario
                WHERE correo = :correo AND rol = 'vendedor'
            """),
            {"correo": vendedor_correo},
        ).scalar_one_or_none()
        if id_vendedor is None:
            raise LookupError("No se encontró el usuario vendedor")

        resultado_articulo = db.execute(
            text("""
                INSERT INTO articulo (
                    titulo, descripcion, condicion,
                    categoria_id_categoria, usuario_id_vendedor
                )
                VALUES (
                    :titulo, :descripcion, :condicion,
                    :id_categoria, :id_vendedor
                )
            """),
            {
                "titulo": data["titulo"],
                "descripcion": data["descripcion"],
                "condicion": data["condicion"],
                "id_categoria": id_categoria,
                "id_vendedor": id_vendedor,
            },
        )
        id_articulo = resultado_articulo.lastrowid
        if id_articulo is None:
            raise RuntimeError("No se obtuvo el ID del artículo creado")

        db.execute(
            text("""
                INSERT INTO imagen_articulo (url, articulo_id_articulo)
                VALUES (:url, :id_articulo)
            """),
            [
                {"url": url, "id_articulo": id_articulo}
                for url in imagenes
            ],
        )

        resultado_subasta = db.execute(
            text("""
                INSERT INTO subasta (
                    precio_inicial, incremento_minimo,
                    fecha_inicio, fecha_fin, estado, articulo_id_articulo
                )
                VALUES (
                    :precio_inicial, :incremento_minimo,
                    :fecha_inicio, :fecha_fin, :estado, :id_articulo
                )
            """),
            {
                "precio_inicial": data["precio_inicial"],
                "incremento_minimo": data["incremento_minimo"],
                "fecha_inicio": data["fecha_inicio"],
                "fecha_fin": data["fecha_fin"],
                "estado": data["estado"],
                "id_articulo": id_articulo,
            },
        )
        id_subasta = resultado_subasta.lastrowid
        if id_subasta is None:
            raise RuntimeError("No se obtuvo el ID de la subasta creada")

        return {
            "id_articulo": id_articulo,
            "id_subasta": id_subasta,
            "imagenes_creadas": len(imagenes),
        }


def crear_articulo(data , id_categoria, id_vendedor, json_imagenes):
    db: Session = next(get_db())
    try:
        # 1. Insertar primero los datos generales en la tabla 'articulo'
        query_articulo = text("""
            INSERT INTO articulo (titulo, descripcion, condicion, imagenURL, categoria_id_categoria, usuario_id_usuario)
            VALUES (:titulo, :descripcion, :condicion, :imagen_url, :id_categoria, :id_vendedor)
        """)
        
        if "imagen_url" in data and data["imagen_url"]:
            if hasattr(data["imagen_url"], "strftime"):
                data["imagen_url"] = data["imagen_url"].strftime('%Y-%m-%d %H:%M:%S')

        resultado = db.execute(
            query_articulo,
            {
                **data,
                "id_categoria": id_categoria,
                "id_vendedor": id_vendedor,
                "imagen_url": json_imagenes,
            },
        )
        
        # Obtenemos el ID autoincrementable que se acaba de crear en 'articulo'
        id_articulo = resultado.lastrowid
        
        db.commit()
        return (True, id_articulo)
    except Exception as err:
        print(f"❌ Error detallado en la base de datos: {err}")
        db.rollback()
        return False
    

def crear_subasta(data, id_articulo, id_vendedor):
    db: Session = next(get_db())
    try:
        # 1. Insertar primero los datos generales en la tabla 'articulo'
        query_subasta = text("""
            INSERT INTO subasta (precio_inicial, incremento_minimo, precio_actual, fecha_inicio, fecha_fin, estado, articulo_id_articulo, usuario_id_usuario1)
            VALUES (:precio_inicial, :incremento_minimo, :precio_actual, :fecha_inicio, :fecha_fin, :estado, :id_articulo, :id_vendedor)
        """)
        
        if "imagen_url" in data and data["imagen_url"]:
            if hasattr(data["imagen_url"], "strftime"):  
                data["imagen_url"] = data["imagen_url"].strftime('%Y-%m-%d %H:%M:%S')   
                
        db.execute(query_subasta, {
            **data,
            "id_articulo": id_articulo,
            "id_vendedor": id_vendedor,
        })
        db.commit()
        return True
    except Exception as err:
        print(f"❌ Error detallado en la base de datos: {err}")
        db.rollback()
        return False




####

def obtener_id_catergoria(categoria):
    db: Session = next(get_db())
    try:
        query = text("SELECT id_categoria FROM categoria WHERE nombre = :categoria")
        result = db.execute(query, {"categoria": categoria}).fetchone()
        if result:
            return result[0]  # Devuelve el id_categoria
        else:
            return None  # No se encontró la categoría
    except Exception as err:
        print(f"❌ Error al obtener el id de la categoría: {err}")
        return None
    

def eliminar_articulo(id_articulo):
    db: Session = next(get_db())
    try:
        query = text("DELETE FROM articulo WHERE id_articulo = :id_articulo")
        db.execute(query, {"id_articulo": id_articulo})
        db.commit()
        return True
    except Exception as err:
        print(f"❌ Error al eliminar el articulo: {err}")
        db.rollback()
        return False
    

def eliminar_subasta_con_id(id_subasta, vendedor_correo):
    db: Session = next(get_db())
    try:
        query = text("DELETE FROM subasta WHERE id_subasta = :id_subasta")
        db.execute(query, {"id_subasta": id_subasta})
        db.commit()
        return True
    except Exception as err:
        print(f"❌ Error al eliminar la subasta: {err}")
        db.rollback()


def eliminar_subasta_y_articulo(id_subasta):
    with SessionLocal.begin() as db:
        id_articulo = db.execute(
            text("""
                SELECT articulo_id_articulo
                FROM subasta
                WHERE id_subasta = :id_subasta
                FOR UPDATE
            """),
            {"id_subasta": id_subasta},
        ).scalar_one_or_none()
        if id_articulo is None:
            raise LookupError("No existe una subasta con ese ID")

        resultado_subasta = db.execute(
            text("DELETE FROM subasta WHERE id_subasta = :id_subasta"),
            {"id_subasta": id_subasta},
        )
        if resultado_subasta.rowcount != 1:
            raise LookupError("No se pudo encontrar la subasta para eliminar")

        resultado_articulo = db.execute(
            text("DELETE FROM articulo WHERE id_articulo = :id_articulo"),
            {"id_articulo": id_articulo},
        )
        if resultado_articulo.rowcount != 1:
            raise RuntimeError("No se pudo eliminar el artículo de la subasta")


def cancelar_subasta(id_subasta, vendedor_correo):
    with SessionLocal.begin() as db:
        subasta = db.execute(
            text("""
                SELECT
                    s.estado,
                    s.fecha_inicio,
                    s.fecha_fin,
                    s.precio_inicial,
                    a.usuario_id_vendedor,
                    NOW() AS fecha_actual
                FROM subasta AS s
                JOIN articulo AS a ON a.id_articulo = s.articulo_id_articulo
                WHERE s.id_subasta = :id_subasta
                FOR UPDATE
            """),
            {"id_subasta": id_subasta},
        ).mappings().one_or_none()

        if subasta is None:
            raise LookupError("No existe una subasta con ese ID")

        id_vendedor = db.execute(
            text("""
                SELECT id_usuario
                FROM usuario
                WHERE correo = :correo AND rol = 'vendedor'
            """),
            {"correo": vendedor_correo},
        ).scalar_one_or_none()
        if id_vendedor is None or id_vendedor != subasta["usuario_id_vendedor"]:
            raise PermissionError("No tienes permiso para cancelar esta subasta")

        validar_programacion(
            subasta["fecha_inicio"],
            subasta["fecha_fin"],
            subasta["precio_inicial"],
        )

        if subasta["estado"] == "cancelada":
            return

        if subasta["estado"] == "terminada" or subasta["fecha_fin"] <= subasta["fecha_actual"]:
            raise ValueError("No se puede cancelar una subasta que ya terminó")

        resultado = db.execute(
            text("""
                UPDATE subasta
                SET estado = 'cancelada', usuario_id_ganador = NULL
                WHERE id_subasta = :id_subasta
                  AND estado IN ('por_empezar', 'en_curso')
            """),
            {"id_subasta": id_subasta},
        )
        if resultado.rowcount != 1:
            raise ValueError("La subasta ya no se encuentra disponible para cancelación")


def actualizar_estados_subastas():
    resumen = {
        "por_empezar": 0,
        "en_curso": 0,
        "terminada": 0,
        "cancelada": 0,
    }
    subastas_por_cerrar = []

    with SessionLocal.begin() as db:
        fecha_actual = db.execute(text("SELECT NOW()")).scalar_one()
        subastas = db.execute(
            text("""
                SELECT id_subasta, precio_inicial, fecha_inicio, fecha_fin
                FROM subasta
                WHERE estado IN ('por_empezar', 'en_curso')
                ORDER BY fecha_fin ASC, id_subasta ASC
                FOR UPDATE
            """)
        ).mappings().all()

        for subasta in subastas:
            fecha_inicio, fecha_fin, precio_inicial = validar_programacion(
                subasta["fecha_inicio"],
                subasta["fecha_fin"],
                subasta["precio_inicial"],
            )

            if fecha_actual < fecha_inicio:
                estado = "por_empezar"
                ganador_id = None
            elif fecha_actual < fecha_fin:
                estado = "en_curso"
                ganador_id = None
            else:
                subastas_por_cerrar.append({
                    "id_subasta": subasta["id_subasta"],
                    "precio_inicial": precio_inicial,
                })
                continue

            resultado = db.execute(
                text("""
                    UPDATE subasta
                    SET estado = :estado, usuario_id_ganador = :ganador_id
                    WHERE id_subasta = :id_subasta
                      AND estado IN ('por_empezar', 'en_curso')
                """),
                {
                    "estado": estado,
                    "ganador_id": ganador_id,
                    "id_subasta": subasta["id_subasta"],
                },
            )
            if resultado.rowcount != 1:
                raise RuntimeError(
                    f"No se pudo actualizar el estado de la subasta {subasta['id_subasta']}"
                )

            resumen[estado] += 1

    for subasta in subastas_por_cerrar:
        try:
            id_subasta = subasta["id_subasta"]
            puja_final = _obtener_ultima_puja(id_subasta)
            ganador_id = None
            monto_final = None
            resultado_pago = None

            if puja_final is not None:
                monto_ganador = validar_monto(
                    puja_final["monto"],
                    "monto de la última puja",
                )
                id_usuario = int(puja_final["usuario_id_usuario"])
                if comparar_montos(monto_ganador, subasta["precio_inicial"]) >= 0:
                    resultado_pago = _crear_pago_pendiente(
                        id_subasta, monto_ganador, id_usuario
                    )
                    ganador_id = id_usuario
                    monto_final = monto_ganador

            with SessionLocal.begin() as db:
                subasta_actual = db.execute(
                    text("""
                        SELECT estado, fecha_fin, NOW() AS fecha_actual
                        FROM subasta
                        WHERE id_subasta = :id_subasta
                        FOR UPDATE
                    """),
                    {"id_subasta": id_subasta},
                ).mappings().one_or_none()

                if (
                    subasta_actual is None
                    or subasta_actual["estado"] not in ("por_empezar", "en_curso")
                    or subasta_actual["fecha_fin"] > subasta_actual["fecha_actual"]
                ):
                    continue

                resultado = db.execute(
                    text("""
                        UPDATE subasta
                        SET estado = 'terminada', usuario_id_ganador = :ganador_id
                        WHERE id_subasta = :id_subasta
                          AND estado IN ('por_empezar', 'en_curso')
                    """),
                    {"ganador_id": ganador_id, "id_subasta": id_subasta},
                )
                if resultado.rowcount != 1:
                    raise RuntimeError(
                        f"No se pudo finalizar la subasta {id_subasta}"
                    )

            resumen["terminada"] += 1
            logger.info(
                "Cierre automático completado: subasta=%s estado=terminada "
                "ganador=%s monto_final=%s pago=%s",
                id_subasta,
                ganador_id if ganador_id is not None else "sin_ganador",
                monto_final if monto_final is not None else "sin_pago",
                (
                    "creado"
                    if resultado_pago and resultado_pago.get("creado")
                    else "reutilizado"
                    if resultado_pago
                    else "no_requerido"
                ),
            )
        except Exception:
            logger.exception(
                "No se pudo finalizar la subasta %s; se volverá a intentar",
                subasta["id_subasta"],
            )

    return resumen



def modificar_subasta(data, id_subasta, correo):
    campos_permitidos = {
        "precio_inicial",
        "incremento_minimo",
        "fecha_inicio",
        "fecha_fin",
        "estado",
    }
    if not data or not set(data).issubset(campos_permitidos):
        raise ValueError("Debe proporcionar al menos un campo permitido para modificar")
    if any(valor is None for valor in data.values()):
        raise ValueError("Los campos enviados para modificar no pueden ser nulos")

    with SessionLocal.begin() as db:
        subasta = db.execute(
            text("""
                SELECT
                    s.precio_inicial,
                    s.incremento_minimo,
                    s.fecha_inicio,
                    s.fecha_fin,
                    s.estado,
                    a.usuario_id_vendedor
                FROM subasta AS s
                JOIN articulo AS a ON a.id_articulo = s.articulo_id_articulo
                WHERE s.id_subasta = :id_subasta
                FOR UPDATE
            """),
            {"id_subasta": id_subasta},
        ).mappings().one_or_none()
        if subasta is None:
            raise LookupError("No existe una subasta con ese ID")

        id_vendedor = db.execute(
            text("""
                SELECT id_usuario
                FROM usuario
                WHERE correo = :correo AND rol = 'vendedor'
            """),
            {"correo": correo},
        ).scalar_one_or_none()
        if id_vendedor is None or id_vendedor != subasta["usuario_id_vendedor"]:
            raise PermissionError("No tienes permiso para modificar esta subasta")

        valores_finales = {
            campo: data.get(campo, subasta[campo])
            for campo in (
                "precio_inicial",
                "incremento_minimo",
                "fecha_inicio",
                "fecha_fin",
                "estado",
            )
        }
        if valores_finales["precio_inicial"] < 0:
            raise ValueError("El precio inicial no puede ser negativo")
        if valores_finales["incremento_minimo"] <= 0:
            raise ValueError("El incremento mínimo debe ser mayor que cero")
        if valores_finales["estado"] not in ("en_curso", "por_empezar"):
            raise ValueError("El estado debe ser 'en_curso' o 'por_empezar'")

        fecha_inicio = valores_finales["fecha_inicio"]
        fecha_fin = valores_finales["fecha_fin"]
        if fecha_inicio.tzinfo != fecha_fin.tzinfo:
            raise ValueError("Las fechas de inicio y fin deben usar la misma zona horaria")
        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

        asignaciones = ", ".join(
            f"{campo} = :{campo}" for campo in data
        )
        db.execute(
            text(f"""
                UPDATE subasta AS s
                SET {asignaciones}
                WHERE s.id_subasta = :id_subasta
                  AND EXISTS (
                      SELECT 1
                      FROM articulo AS a
                      JOIN usuario AS u
                        ON u.id_usuario = a.usuario_id_vendedor
                      WHERE a.id_articulo = s.articulo_id_articulo
                        AND u.id_usuario = :id_vendedor
                        AND u.correo = :correo
                        AND u.rol = 'vendedor'
                  )
            """),
            {
                **data,
                "id_subasta": id_subasta,
                "id_vendedor": id_vendedor,
                "correo": correo,
            },
        )