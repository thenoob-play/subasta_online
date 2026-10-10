from sqlalchemy import text

from DataBase.connection import SessionLocal


MAX_ARTICULOS_POR_BUSQUEDA = 50


def buscar_articulos(filtros):
    condiciones = []
    parametros = {"limite": MAX_ARTICULOS_POR_BUSQUEDA}

    if filtros.get("nombre") is not None:
        condiciones.append("LOCATE(LOWER(:nombre), LOWER(a.titulo)) > 0")
        parametros["nombre"] = filtros["nombre"]

    if filtros.get("categoria") is not None:
        condiciones.append("LOWER(c.nombre) = LOWER(:categoria)")
        parametros["categoria"] = filtros["categoria"]

    if filtros.get("precio_inicial") is not None:
        condiciones.append("s.precio_inicial >= :precio_inicial")
        parametros["precio_inicial"] = filtros["precio_inicial"]

    if filtros.get("precio_final") is not None:
        condiciones.append("s.precio_inicial <= :precio_final")
        parametros["precio_final"] = filtros["precio_final"]

    if filtros.get("fecha_inicio") is not None:
        condiciones.append("s.fecha_fin >= :fecha_inicio")
        parametros["fecha_inicio"] = filtros["fecha_inicio"]

    if filtros.get("fecha_fin") is not None:
        condiciones.append("s.fecha_inicio <= :fecha_fin")
        parametros["fecha_fin"] = filtros["fecha_fin"]

    where_clause = (
        f"WHERE {' AND '.join(condiciones)}"
        if condiciones
        else ""
    )
    query = text(f"""
        SELECT
            seleccion.id_subasta,
            seleccion.id_articulo,
            seleccion.titulo,
            seleccion.descripcion,
            seleccion.condicion,
            seleccion.categoria,
            seleccion.precio_inicial,
            seleccion.incremento_minimo,
            seleccion.fecha_inicio,
            seleccion.fecha_fin,
            seleccion.estado,
            imagen.url AS imagen_url
        FROM (
            SELECT
                s.id_subasta,
                a.id_articulo,
                a.titulo,
                a.descripcion,
                a.condicion,
                c.nombre AS categoria,
                s.precio_inicial,
                s.incremento_minimo,
                s.fecha_inicio,
                s.fecha_fin,
                s.estado
            FROM subasta AS s
            INNER JOIN articulo AS a
                ON a.id_articulo = s.articulo_id_articulo
            INNER JOIN categoria AS c
                ON c.id_categoria = a.categoria_id_categoria
            {where_clause}
            ORDER BY s.id_subasta DESC
            LIMIT :limite
        ) AS seleccion
        LEFT JOIN imagen_articulo AS imagen
            ON imagen.articulo_id_articulo = seleccion.id_articulo
        ORDER BY seleccion.id_subasta DESC, imagen.id_imagen ASC
    """)

    with SessionLocal() as db:
        filas = db.execute(query, parametros).mappings().all()

    resultados = {}
    for fila in filas:
        id_subasta = fila["id_subasta"]
        articulo = resultados.setdefault(
            id_subasta,
            {
                "id_subasta": id_subasta,
                "id_articulo": fila["id_articulo"],
                "titulo": fila["titulo"],
                "descripcion": fila["descripcion"],
                "condicion": fila["condicion"],
                "categoria": fila["categoria"],
                "precio_inicial": fila["precio_inicial"],
                "incremento_minimo": fila["incremento_minimo"],
                "fecha_inicio": fila["fecha_inicio"],
                "fecha_fin": fila["fecha_fin"],
                "estado": fila["estado"],
                "imagenes": [],
            },
        )
        if fila["imagen_url"] is not None:
            articulo["imagenes"].append(fila["imagen_url"])

    return list(resultados.values())
