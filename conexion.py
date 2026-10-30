# CÓDIGO AGREGADO POR CODEX
"""Acceso a PF2etapa. Solo contiene consultas parametrizadas y transacciones."""
import os
from pathlib import Path
from contextlib import contextmanager

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # Permite abrir el menú y usar las clases sin el conector.
    mysql = None
    Error = Exception


def conectar_mysql():
    if mysql is None:
        raise RuntimeError("Falta mysql-connector-python. Instalalo con: python -m pip install mysql-connector-python")
    # CÓDIGO AGREGADO POR CODEX: lee .env local (ignorado por Git) sin dependencias adicionales.
    archivo_env = Path(__file__).with_name(".env")
    if archivo_env.exists():
        for linea in archivo_env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip().strip('"\''))
    configuracion = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "PF2etapa"),
        "connection_timeout": 5,
    }
    if not configuracion["password"]:
        raise RuntimeError("Configurá MYSQL_PASSWORD en las variables de entorno.")
    return mysql.connector.connect(**configuracion)


@contextmanager
def cursor_db(diccionario=False):
    conexion = conectar_mysql()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=diccionario)
        yield conexion, cursor
    except Exception:
        if conexion.is_connected():
            conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


# CÓDIGO AGREGADO POR CODEX: validaciones acordes a los VARCHAR e INT del esquema consultado.
def _validar_texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede quedar vacío.")
    if len(valor.strip()) > 50:
        raise ValueError(f"{campo} admite hasta 50 caracteres según la base de datos.")
    return valor.strip()


def _validar_id(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError(f"{campo} debe ser un entero positivo.")
    return valor


def _validar_precio(precio):
    from decimal import Decimal, InvalidOperation
    try:
        precio = Decimal(str(precio))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("El precio debe ser un entero no negativo.") from exc
    if not precio.is_finite() or precio < 0 or precio != precio.to_integral_value() or precio > 2147483647:
        raise ValueError("El precio debe ser un entero no negativo admitido por MySQL.")
    return int(precio)


def _validar_telefono(cel):
    if isinstance(cel, bool) or not isinstance(cel, int) or not 0 <= cel <= 2147483647:
        raise ValueError("El teléfono debe ser un entero entre 0 y 2147483647 según la columna cel.")
    return cel


def verificar_esquema(cursor):
    """Valida las columnas conocidas antes de ejecutar operaciones CRUD."""
    esperado = {
        "producto": {"id", "nombre_producto", "precio", "stock", "id_provedor", "marca", "perecedero"},
        "provedor": {"id", "nombre_empresa", "cel", "ubicacion"},
        "movimientos": {"idmov", "id_producto", "cantidad", "fecha_hora", "tipo_mov"},
    }
    for tabla, requeridas in esperado.items():
        cursor.execute(f"DESCRIBE `{tabla}`")
        filas = cursor.fetchall()
        existentes = {fila["Field"] if isinstance(fila, dict) else fila[0] for fila in filas}
        if not requeridas.issubset(existentes):
            faltan = ", ".join(sorted(requeridas - existentes))
            raise RuntimeError(f"Esquema inesperado en {tabla}; faltan columnas: {faltan}")


def _producto(fila):
    from poo import Producto, Proveedor
    proveedor = Proveedor(fila["id_provedor"], fila.get("nombre_empresa") or "", fila.get("ubicacion") or "", fila.get("cel") or "")
    return Producto(fila["id"], fila["nombre_producto"], fila["precio"], fila["stock"], marca=fila.get("marca") or "No informada", proveedor=proveedor, perecedero=bool(fila.get("perecedero", False)))


# CÓDIGO AGREGADO POR CODEX: columnas comunes para convertir filas de productos.
_COLUMNAS_PRODUCTO = "p.id,p.nombre_producto,p.precio,p.stock,p.id_provedor,p.marca,p.perecedero,v.nombre_empresa,v.ubicacion,v.cel"


def _proveedor(fila):
    from poo import Proveedor
    return Proveedor(fila["id"], fila["nombre_empresa"], fila["ubicacion"], fila["cel"])


def listar_productos():
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute(f"SELECT {_COLUMNAS_PRODUCTO} FROM producto p LEFT JOIN provedor v ON p.id_provedor=v.id ORDER BY p.id")
        return [_producto(x) for x in cur.fetchall()]


def buscar_producto(id_producto):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute(f"SELECT {_COLUMNAS_PRODUCTO} FROM producto p LEFT JOIN provedor v ON p.id_provedor=v.id WHERE p.id=%s", (id_producto,))
        fila = cur.fetchone()
        return _producto(fila) if fila else None


def productos_de_proveedor(id_proveedor):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute(f"SELECT {_COLUMNAS_PRODUCTO} FROM producto p JOIN provedor v ON p.id_provedor=v.id WHERE v.id=%s ORDER BY p.id", (id_proveedor,))
        return [_producto(x) for x in cur.fetchall()]


def proveedor_de_producto(id_producto):
    producto = buscar_producto(id_producto)
    return producto.proveedor if producto else None


def listar_proveedores():
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_empresa,cel,ubicacion FROM provedor ORDER BY id")
        return [_proveedor(x) for x in cur.fetchall()]


def buscar_proveedor(id_proveedor):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_empresa,cel,ubicacion FROM provedor WHERE id=%s", (id_proveedor,))
        fila = cur.fetchone()
        return _proveedor(fila) if fila else None


def _guardar(sql, parametros):
    with cursor_db() as (conexion, cur):
        verificar_esquema(cur)
        cur.execute(sql, parametros)
        conexion.commit()
        return cur.lastrowid, cur.rowcount


def crear_producto(nombre, precio, stock, id_proveedor, marca="No informada", perecedero=False):
    nombre = _validar_texto(nombre, "El nombre")
    marca = _validar_texto(marca, "La marca")
    if not isinstance(perecedero, bool):
        raise ValueError("El estado perecedero debe ser Sí o No.")
    precio = _validar_precio(precio)
    if isinstance(stock, bool) or not isinstance(stock, int) or not 0 <= stock <= 2147483647:
        raise ValueError("El stock inicial debe ser un entero no negativo.")
    _validar_id(id_proveedor, "El ID del proveedor")
    if buscar_proveedor(id_proveedor) is None:
        raise ValueError("El proveedor indicado no existe.")
    nuevo_id, _ = _guardar("INSERT INTO producto (nombre_producto,marca,perecedero,precio,stock,id_provedor) VALUES (%s,%s,%s,%s,%s,%s)", (nombre, marca, perecedero, precio, stock, id_proveedor))
    return buscar_producto(nuevo_id)


def actualizar_producto(id_producto, nombre, precio, id_proveedor, marca=None, perecedero=None, stock=None):
    _validar_id(id_producto, "El ID del producto")
    anterior = buscar_producto(id_producto)
    if anterior is None:
        return None
    nombre = _validar_texto(anterior.nombre if nombre is None else nombre, "El nombre")
    marca = _validar_texto(anterior.marca if marca is None else marca, "La marca")
    precio = _validar_precio(anterior.precio if precio is None else precio)
    id_proveedor = anterior.proveedor.id if id_proveedor is None else id_proveedor
    _validar_id(id_proveedor, "El ID del proveedor")
    perecedero = anterior.perecedero if perecedero is None else perecedero
    if not isinstance(perecedero, bool):
        raise ValueError("El estado perecedero debe ser Sí o No.")
    stock = anterior.stock if stock is None else stock
    if isinstance(stock, bool) or not isinstance(stock, int) or not 0 <= stock <= 2147483647:
        raise ValueError("El stock debe ser un entero no negativo.")
    if buscar_proveedor(id_proveedor) is None:
        raise ValueError("El proveedor indicado no existe.")
    # CÓDIGO AGREGADO POR CODEX: una edición de stock también deja su movimiento en la misma transacción.
    with cursor_db(True) as (db, cur):
        verificar_esquema(cur)
        cur.execute("SELECT stock FROM producto WHERE id=%s FOR UPDATE", (id_producto,))
        fila_stock = cur.fetchone()
        if fila_stock is None:
            return None
        stock_anterior = fila_stock["stock"]
        cur.execute("UPDATE producto SET nombre_producto=%s,marca=%s,perecedero=%s,precio=%s,stock=%s,id_provedor=%s WHERE id=%s", (nombre, marca, perecedero, precio, stock, id_proveedor, id_producto))
        if stock != stock_anterior:
            tipo = "ENTRADA" if stock > stock_anterior else "SALIDA"
            cur.execute("INSERT INTO movimientos (id_producto,cantidad,fecha_hora,tipo_mov) VALUES (%s,%s,NOW(),%s)", (id_producto, abs(stock - stock_anterior), tipo))
        db.commit()
    return buscar_producto(id_producto)


def eliminar_producto(id_producto):
    _, cuenta = _guardar("DELETE FROM producto WHERE id=%s", (id_producto,))
    return cuenta > 0


def cambiar_stock(id_producto, cantidad, aumentar):
    # CÓDIGO AGREGADO POR CODEX: conserva la función anterior y registra todo cambio como movimiento.
    try:
        _, producto = registrar_movimiento(id_producto, cantidad, "ENTRADA" if aumentar else "SALIDA")
        return producto
    except ValueError as error:
        if "No existe un producto" in str(error):
            return None
        raise


# CÓDIGO AGREGADO POR CODEX: stock e historial se confirman o revierten juntos.
def registrar_movimiento(id_producto, cantidad, tipo):
    _validar_id(id_producto, "El ID del producto")
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("La cantidad debe ser un entero positivo.")
    tipo = str(tipo).strip().upper()
    if tipo not in ("ENTRADA", "SALIDA"):
        raise ValueError("El tipo debe ser ENTRADA o SALIDA.")
    with cursor_db(True) as (db, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_producto,marca,perecedero,precio,stock,id_provedor FROM producto WHERE id=%s FOR UPDATE", (id_producto,))
        fila = cur.fetchone()
        if fila is None:
            raise ValueError("No existe un producto con ese identificador.")
        from poo import Producto, Movimientos_Stock
        producto = Producto(fila["id"], fila["nombre_producto"], fila["precio"], fila["stock"], marca=fila["marca"], proveedor=fila["id_provedor"], perecedero=bool(fila["perecedero"]))
        nuevo_stock = producto.aumentar_stock(cantidad) if tipo == "ENTRADA" else producto.disminuir_stock(cantidad)
        if nuevo_stock is False:
            raise ValueError("No hay stock suficiente para realizar esa salida.")
        cur.execute("UPDATE producto SET stock=%s WHERE id=%s", (nuevo_stock, id_producto))
        cur.execute("INSERT INTO movimientos (id_producto,cantidad,fecha_hora,tipo_mov) VALUES (%s,%s,NOW(),%s)", (id_producto, cantidad, tipo))
        movimiento = Movimientos_Stock(cur.lastrowid, tipo, producto, cantidad)
        producto.actualizar_stock(nuevo_stock)
        cur.execute("SELECT fecha_hora FROM movimientos WHERE idmov=%s", (movimiento.id,))
        movimiento.fecha_hora = cur.fetchone()["fecha_hora"]
        movimiento.fecha = movimiento.fecha_hora.date()
        movimiento.hora = movimiento.fecha_hora.time()
        db.commit()
        return movimiento, producto


def listar_movimientos(id_producto=None):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        sql = "SELECT m.idmov,m.tipo_mov,m.cantidad,m.fecha_hora,p.id AS producto_id,p.nombre_producto FROM movimientos m LEFT JOIN producto p ON p.id=m.id_producto"
        parametros = ()
        if id_producto is not None:
            _validar_id(id_producto, "El ID del producto")
            sql += " WHERE m.id_producto=%s"
            parametros = (id_producto,)
        sql += " ORDER BY m.fecha_hora DESC,m.idmov DESC"
        cur.execute(sql, parametros)
        return cur.fetchall()


def crear_proveedor(nombre, cel, ubicacion):
    nombre = _validar_texto(nombre, "El nombre de la empresa")
    ubicacion = _validar_texto(ubicacion, "La ubicación")
    cel = _validar_telefono(cel)
    nuevo_id, _ = _guardar("INSERT INTO provedor (nombre_empresa,cel,ubicacion) VALUES (%s,%s,%s)", (nombre, cel, ubicacion))
    return buscar_proveedor(nuevo_id)


def actualizar_proveedor(id_proveedor, nombre, cel, ubicacion):
    _validar_id(id_proveedor, "El ID del proveedor")
    nombre = _validar_texto(nombre, "El nombre de la empresa")
    ubicacion = _validar_texto(ubicacion, "La ubicación")
    cel = _validar_telefono(cel)
    if buscar_proveedor(id_proveedor) is None:
        return None
    _guardar("UPDATE provedor SET nombre_empresa=%s,cel=%s,ubicacion=%s WHERE id=%s", (nombre, cel, ubicacion, id_proveedor))
    return buscar_proveedor(id_proveedor)


def eliminar_proveedor(id_proveedor):
    with cursor_db(True) as (conexion, cur):
        verificar_esquema(cur)
        cur.execute("SELECT COUNT(*) AS cantidad FROM producto WHERE id_provedor=%s", (id_proveedor,))
        if cur.fetchone()["cantidad"]:
            raise ValueError("El proveedor tiene productos asociados; resolvé esa relación antes de eliminarlo.")
        cur.execute("DELETE FROM provedor WHERE id=%s", (id_proveedor,))
        conexion.commit()
        return cur.rowcount > 0
