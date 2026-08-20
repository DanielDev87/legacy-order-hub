# Arquitectura Hexagonal aplicada a Legacy OrderHub

## Objetivo
Para la primera entrega, se aplica una refactorización mínima para desacoplar la lógica de autenticación de la capa HTTP y del acceso directo a SQLite.

## Capas

### 1. Dominio
Contiene la entidad de usuario como modelo de negocio simple.

- `domain/user.py`

### 2. Repositorios
Encapsula el acceso a persistencia en SQLite para consultar al usuario por credenciales.

- `repositories/user_repository.py`

### 3. Servicios
Contiene la lógica de autenticación.

- `services/auth_service.py`

### 4. Adaptadores HTTP
La capa HTTP (`app.py`) solo recibe la solicitud y delega la validación al servicio.

## Beneficios
- Reduce el acoplamiento entre Flask y SQLite.
- Facilita pruebas unitarias y revisión del código.
- Deja una base clara para futuras extensiones del sistema.

## Diagrama conceptual

```text
+-------------------+
| HTTP / Flask      |
| app.py            |
+---------+---------+
          |
          v
+-------------------+
| Services          |
| auth_service.py   |
+---------+---------+
          |
          v
+-------------------+
| Repositories      |
| user_repository.py|
+---------+---------+
          |
          v
+-------------------+
| SQLite / Database |
+-------------------+
```
