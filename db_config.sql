CREATE DATABASE libreria;

USE libreria;

CREATE TABLE libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100),
    autor VARCHAR(100),
    editorial VARCHAR(100),
    precio DECIMAL(10, 2)
);
