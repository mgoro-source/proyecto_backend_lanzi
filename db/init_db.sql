DROP TABLE if EXISTS deportes;
CREATE TABLE deportes
(
id_deporte INT AUTO_INCREMENT PRIMARY KEY,
nombre_deporte VARCHAR (10) NOT NULL
);


DROP TABLE if EXISTS socios;
CREATE TABLE socios
(
id_socio INT AUTO_INCREMENT PRIMARY KEY,
nombre_socio VARCHAR (50) NOT NULL,
email_socio VARCHAR (50) NOT NULL,
activo BOOLEAN NOT NULL DEFAULT TRUE
);

DROP TABLE if EXISTS canchas;
CREATE TABLE canchas
(
id_cancha INT AUTO_INCREMENT PRIMARY KEY,
nombre_cancha VARCHAR (50) NOT NULL,
techada BOOLEAN NOT NULL DEFAULT FALSE,
precio_hora INT NOT NULL,
activa BOOLEAN NOT NULL DEFAULT TRUE,
id_deporte_cancha INT,
    CONSTRAINT fk_cancha_deporte FOREIGN KEY (id_deporte_cancha) 
        REFERENCES deportes(id_deporte)
        ON DELETE SET NULL
        ON UPDATE CASCADE

) ENGINE=InnoDB;

DROP TABLE if EXISTS reservas;
CREATE TABLE reservas
(
id_reserva INT AUTO_INCREMENT PRIMARY KEY,
estado_actual VARCHAR (50) NOT NULL,
estado_solicitado VARCHAR (50) NOT NULL,
condicion VARCHAR (50) NOT NULL,
fecha_reserva_inicio DATETIME(6) NOT NULL, 
fecha_iso_inicio VARCHAR(35) GENERATED ALWAYS AS (
        CONCAT(DATE_FORMAT(fecha_reserva_inicio, '%Y-%m-%dT%H:%i:%s.%f'), '-03:00')
    ) VIRTUAL,
fecha_reserva_fin DATETIME(6) NOT NULL, 
fecha_iso_fin VARCHAR(35) GENERATED ALWAYS AS (
        CONCAT(DATE_FORMAT(fecha_reserva_fin, '%Y-%m-%dT%H:%i:%s.%f'), '-03:00')
    ) VIRTUAL,
duracion_horas INT GENERATED ALWAYS AS (TIMESTAMPDIFF(HOUR, fecha_reserva_inicio, fecha_reserva_fin)) STORED,
precio_hora INT NOT NULL,
importe_total INT GENERATED ALWAYS AS (precio_hora * duracion_horas) STORED,
id_cancha_reserva INT, 
id_socio_reserva INT,
    CONSTRAINT fk_reserva_cancha FOREIGN KEY (id_cancha_reserva) 
        REFERENCES canchas(id_cancha)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_reserva_socio FOREIGN KEY (id_socio_reserva) 
        REFERENCES socios(id_socio)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

INSERT INTO deportes (nombre_deporte)
VALUES
('Futbol'),
('Tenis' ),
('Padel');

INSERT INTO socios (nombre_socio, email_socio, activo)
VALUES
('Juan Perez', 'jp@hotmail.com'),
( 'Maria Lopez', 'ml@gmail.com', FALSE ),
('Lucas Gomez', 'lg@gmail.com');

INSERT INTO canchas (nombre_cancha, techada, precio_hora, activa, id_deporte_cancha)
VALUES
('Diego Maradona', TRUE, 1000, TRUE, 1),
('Guillermo Vilas',FALSE,  2000, FALSE , 2 ),
('Roby Gattiker', TRUE, 10000, TRUE, 3);


INSERT INTO reservas (estado_actual, estado_solicitado, condicion, fecha_reserva_inicio, fecha_reserva_fin, precio_hora, id_cancha_reserva, id_socio_reserva) VALUES 
('confirmada', 'finalizada', 'El horario no comenzo', '2026-10-25 09:00:00.000000','2026-10-25 12:00:00.000000', 10000, 1, 2),
('confirmada', 'cancelada', 'Se alcanzo', '2026-10-25 09:00:00.000000','2026-10-25 12:00:00.000000', 10000, 3, 1),
('cancelada', 'otro estado', 'No permitido', '2026-10-26 09:00:00.000000','2026-10-26 12:00:00.000000', 55000, 2, 1);

