from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from datetime import datetime
import json

## import a al archivo crudSubasta.py
from backend.ppp.crud.crudSubasta import crear_articulo, obtener_id_catergoria , crear_subasta , eliminar_articulo , eliminar_subasta_con_id
## import a al archivo crudRegirstro.py
from backend.ppp.crud.crudRegirstro import obtener_id_vendedor


def crear_articulos(dato, vendedor_correo):
    titulo = dato["titulo"]
    descripcion = dato["descripcion"]
    condicion = dato["condicion"]    
    imagen_url = dato.get("imagen_url")
    categoria = dato["categoria"]
    
    
    if titulo is None or descripcion is None or condicion is None or imagen_url is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")

    if len(titulo) < 3 or len(descripcion) < 3  or len(imagen_url) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los datos son incorrectos")
    
    #ENUM('bueno', 'medio', 'malo')
    if condicion not in ["nuevo", "medio", "malo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La condición debe ser 'nuevo', 'medio' o 'malo'")
    
    if not isinstance(imagen_url, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="imagen_url debe ser una lista de rutas")
    
    # B. Verificar que la lista no esté vacía
    if len(imagen_url) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe subir al menos una imagen")
    
    # C. Limitar el número máximo de imágenes (ejemplo: máximo 5)
    if len(imagen_url) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes subir más de 5 imágenes")
    
    # D. Validar que cada ruta individual dentro de la lista sea válida
    for url in imagen_url:
        if not isinstance(url, str) or len(url.strip()) < 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Una de las rutas de imagen es inválida")
    
    #obtener el id de la categoría    
    id_categoria = obtener_id_catergoria(categoria)
    if id_categoria is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoría no existe")
    
    #obtener el id del vendedor
    id_vendedor = obtener_id_vendedor(vendedor_correo) 
    
    # E. Convertir la lista de rutas en una cadena de texto JSON
    json_imagenes = json.dumps(imagen_url)    
    
    
    try:
        info_articulo = crear_articulo(dato , id_categoria, id_vendedor, json_imagenes)
        return {
            True,
            info_articulo[1],
            id_vendedor
        }
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear articulo: {err}")
    
    
    
def crear_subasta(dato, vendedor_correo):
    precio_inicial = dato["precio_inicial"]
    incremento_minimo = dato["incremento_minimo"]
    precio_actual = dato["precio_actual"]
    fecha_inicio = dato["fecha_inicio"]
    fecha_fin = dato["fecha_fin"]
    estado = dato["estado"]
    
        
    if precio_inicial is None or incremento_minimo is None or precio_actual is None or fecha_inicio is None or fecha_fin is None or estado is None :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Faltan datos")
    
    if precio_inicial < 0 or incremento_minimo < 0 or precio_actual < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los datos son incorrectos")
    
    if fecha_inicio.replace(second=0, microsecond=0) != datetime.now().replace(
        second=0, microsecond=0
        ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha y hora de inicio deben coincidir con el minuto actual",
        )
        
    
    
    
        
    if fecha_inicio >= fecha_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de inicio debe ser menor a la fecha de fin")
    #ENUM('en_curso', 'por_empezar', 'terminada', 'cancelada')
    if estado not in ["en_curso", "por_empezar"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estado debe ser 'en_curso', 'por_empezar''")
    
    
    creacion_articulos = crear_articulos(dato,vendedor_correo)
    
    if creacion_articulos[0] is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al crear articulo")
    
    
    try:
        creacion_subasta = crear_subasta(dato, creacion_articulos[1], creacion_articulos[2])
        
        if creacion_subasta is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al crear subasta")
        
        return {"message": "Subasta creada correctamente"}
    except Exception as err:
        eliminar_articulo(creacion_articulos[1])
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear subasta: {err}")
    
    
