-- Tabla única y simplificada de reservas
CREATE TABLE IF NOT EXISTS ${db_schema}.reservas (
  id_persona VARCHAR(50) PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  fecha_reserva DATE NOT NULL,
  hora_reserva TIME NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento de las consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON ${db_schema}.reservas (fecha_reserva);
CREATE INDEX IF NOT EXISTS idx_reservas_status ON ${db_schema}.reservas (status);

-- Comentario de la tabla para documentación
COMMENT ON TABLE ${db_schema}.reservas IS 'Tabla principal para almacenar las reservas de clientes';