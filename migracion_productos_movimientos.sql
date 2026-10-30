-- CÓDIGO AGREGADO POR CODEX
-- Migración preparada tras inspeccionar el esquema real existente.
-- Ejecutar una sola vez sobre la base PF2etapa. No recrea tablas ni elimina datos.

ALTER TABLE producto
    ADD COLUMN marca VARCHAR(50) NOT NULL DEFAULT 'No informada',
    ADD COLUMN perecedero BOOLEAN NOT NULL DEFAULT FALSE;

-- Los movimientos existentes conservan sus columnas y relaciones.
-- No se inventan cantidades ni fechas para registros antiguos.
ALTER TABLE movimientos
    ADD COLUMN cantidad INT NULL,
    ADD COLUMN fecha_hora DATETIME NULL;
