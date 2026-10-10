# URLs disponibles de las APIs de SubastaOnline

Este documento relaciona las rutas HTTP disponibles con las tablas que cada API consulta o modifica.

## Bases URL

- **FastAPI:** `http://localhost:8000`
  - Documentación interactiva: `http://localhost:8000/docs`
- **PHP:** depende de Apache/XAMPP y de la configuración del servidor. En los ejemplos se usa `http://localhost`, suponiendo que Apache reenvía `/categoria`, `/puja` y `/historialPuja` a `backend/php/index.php`.
- **Node.js:** `http://localhost:3000` por defecto. Puede cambiar mediante la variable de entorno `PORT`.

Reemplaza `localhost` por la dirección IP o dominio del servidor cuando se acceda desde otro equipo. Los segmentos `{id}` y `{id_subasta}` son marcadores: sustitúyelos por valores reales.

## URLs por tabla de la base de datos

| Tabla | API y rutas relacionadas | Observación |
|---|---|---|
| `usuario` | **FastAPI:** `POST /CrearCuenta`, `POST /Login`, `PUT /ModificarUsuario`, `POST /CrearCuentaVendedor`, `POST /LoginVendedor`. **PHP:** `POST /puja` recibe `usuario_id_usuario`. **Node.js:** `POST /api/pagos/subasta` busca al comprador por correo. | `CrearCuentaVendedor` también registra el perfil extendido en `vendedor`. |
| `vendedor` | **FastAPI:** `POST /CrearCuentaVendedor`. | No hay rutas para consultar, listar o modificar perfiles de vendedor. |
| `categoria` | **PHP:** `GET /categoria`, `GET /categoria/{id}`, `POST /categoria`, `PUT /categoria/{id}`, `PATCH /categoria/{id}`, `DELETE /categoria/{id}`. **FastAPI:** `POST /CrearSubasta`, `POST /CrearSubastaNuevo` y `POST /pedirArticulo` consultan o usan categorías. | El CRUD de categorías está en PHP; FastAPI no ofrece CRUD directo de esta tabla. |
| `articulo` | **FastAPI:** `POST /CrearSubasta`, `POST /CrearSubastaNuevo`, `DELETE /EliminarSubasta`, `POST /pedirArticulo`. | El artículo se crea como parte de una subasta; no hay CRUD independiente. |
| `imagen_articulo` | **FastAPI:** `POST /CrearSubasta`, `POST /CrearSubastaNuevo`, `POST /pedirArticulo`. | Las imágenes se crean junto con el artículo y se incluyen en resultados de búsqueda. |
| `subasta` | **FastAPI:** `POST /CrearSubasta`, `POST /CrearSubastaNuevo`, `DELETE /EliminarSubasta`, `POST /CancelarSubasta`, `PUT /ModificarSubasta`, `POST /pedirArticulo`. **PHP:** `POST /puja` y `GET /puja/ultima/{id_subasta}` consultan o validan la subasta. | El scheduler de FastAPI también actualiza/cierra subastas, pero no es un endpoint HTTP. |
| `puja` | **PHP:** `GET /puja`, `GET /puja/{id}`, `GET /puja/ultima/{id_subasta}`, `POST /puja`, `DELETE /puja/{id}`. | `POST /puja` valida estado, fechas, incremento mínimo y el turno del ofertante. |
| `historial_puja` | **PHP:** `GET /historialPuja`, `GET /historialPuja/{id}`, `POST /historialPuja`. | El endpoint de pujas no registra automáticamente el historial; se escribe mediante `POST /historialPuja`. |
| `pago` | **Node.js:** `GET /api/pagos`, `GET /api/pagos/{id}`, `POST /api/pagos`, `POST /api/pagos/subasta`, `PUT /api/pagos/{id}/anular`. **FastAPI:** el cierre automático llama internamente a `POST /api/pagos/subasta`. Las rutas Node de transferencias también actualizan el pago relacionado. | El cierre automático solicita o reutiliza el pago pendiente de una subasta. |
| `transferencia_pago` | **Node.js:** `GET /api/transferencias`, `GET /api/transferencias/{id}`, `POST /api/transferencias`, `PUT /api/transferencias/{id}/anular`. | La transferencia requiere un pago en espera cuyo método sea `transferencia`. |

## API FastAPI

Base URL: `http://localhost:8000`

| Método | URL | Tablas relacionadas |
|---|---|---|
| `GET` | `/` | Ninguna; comprueba que la API responde. |
| `POST` | `/CrearCuenta` | `usuario` |
| `POST` | `/Login` | `usuario` |
| `PUT` | `/ModificarUsuario` | `usuario` |
| `POST` | `/CrearCuentaVendedor` | `usuario`, `vendedor` |
| `POST` | `/LoginVendedor` | `usuario` |
| `POST` | `/pedirArticulo` | `subasta`, `articulo`, `categoria`, `imagen_articulo` |
| `POST` | `/CrearSubasta` | `usuario`, `categoria`, `articulo`, `imagen_articulo`, `subasta` |
| `POST` | `/CrearSubastaNuevo` | `usuario`, `categoria`, `articulo`, `imagen_articulo`, `subasta` |
| `DELETE` | `/EliminarSubasta` | `subasta`, `articulo` y relaciones aplicables |
| `POST` | `/CancelarSubasta` | `subasta`; valida propiedad mediante `articulo` y `usuario` |
| `PUT` | `/ModificarSubasta` | `subasta`; valida propiedad mediante `articulo` y `usuario` |

`PUT /ModificarUsuario` y `POST /pedirArticulo` requieren token. `POST /CrearSubasta` también requiere token. Las demás rutas indicadas reciben correo/datos en el cuerpo y no comparten todas el mismo requisito de autenticación según la implementación actual.

## API PHP

La base URL depende de la configuración del servidor web. Las rutas de abajo asumen que Apache/XAMPP reenvía los paths al front controller `backend/php/index.php`.

### Categorías — tabla `categoria`

| Método | URL |
|---|---|
| `GET` | `/categoria` |
| `GET` | `/categoria/{id}` |
| `POST` | `/categoria` |
| `PUT` | `/categoria/{id}` |
| `PATCH` | `/categoria/{id}` |
| `DELETE` | `/categoria/{id}` |

### Pujas — tablas `puja`, `subasta` y referencia a `usuario`

| Método | URL |
|---|---|
| `GET` | `/puja` |
| `GET` | `/puja/{id}` |
| `GET` | `/puja/ultima/{id_subasta}` |
| `POST` | `/puja` |
| `DELETE` | `/puja/{id}` |

### Historial — tabla `historial_puja`

| Método | URL |
|---|---|
| `GET` | `/historialPuja` |
| `GET` | `/historialPuja/{id}` |
| `POST` | `/historialPuja` |

## API Node.js

Base URL por defecto: `http://localhost:3000`

### Pagos — tablas `pago` y `usuario` (pago pendiente por subasta)

| Método | URL |
|---|---|
| `GET` | `/api/pagos` |
| `GET` | `/api/pagos/{id}` |
| `POST` | `/api/pagos` |
| `POST` | `/api/pagos/subasta` |
| `PUT` | `/api/pagos/{id}/anular` |

### Transferencias — tablas `transferencia_pago` y `pago`

| Método | URL |
|---|---|
| `GET` | `/api/transferencias` |
| `GET` | `/api/transferencias/{id}` |
| `POST` | `/api/transferencias` |
| `PUT` | `/api/transferencias/{id}/anular` |

## Notas

- Las rutas PHP requieren configuración de virtual host o rewrite. Si se sirve `index.php` bajo otro prefijo, configura el servidor para que las rutas `/categoria`, `/puja` y `/historialPuja` lleguen al front controller.
- La búsqueda de artículos y la creación de subastas de FastAPI consultan varias tablas en una misma operación; la tabla indicada no siempre es la única que participa.
- El scheduler de FastAPI no tiene URL pública. Al cerrar subastas consulta la última puja por PHP y crea/reutiliza el pago pendiente por Node.js.
