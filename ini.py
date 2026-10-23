# CORRECCIÓN DE CODEX
# Compatibilidad con el nombre del archivo de acceso usado anteriormente.
from conexion import (  # noqa: F401
    conectar_mysql, listar_productos, buscar_producto, crear_producto,
    actualizar_producto, eliminar_producto, cambiar_stock,
)


if __name__ == "__main__":
    print("Usá main.py para abrir el menú del sistema.")
