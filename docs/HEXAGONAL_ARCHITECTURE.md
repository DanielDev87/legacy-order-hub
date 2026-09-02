# Arquitectura Hexagonal aplicada a Legacy OrderHub (Django)

## Objetivo
El sistema fue migrado de Flask + SQLite crudo a **Django + Django REST Framework**, aplicando arquitectura hexagonal (ports & adapters) de forma consistente en cada contexto delimitado del dominio. Esta es la base sobre la cual se irán resolviendo las siguientes historias de usuario del backlog (`docs/ANALYSIS_AND_REQUIREMENTS.md`).

## Apps por contexto delimitado
El proyecto se organiza en `apps/`, con un Django app por contexto: `apps/users`, `apps/catalog` (productos) y `apps/orders`. Cada uno replica la misma estructura de capas:

```
apps/<contexto>/
    models.py              # Adaptador de persistencia (modelos ORM de Django)
    migrations/             # Incluye migraciones de datos para el seed inicial
    domain/
        entities.py          # Entidades de negocio (dataclasses puras, sin Django)
        exceptions.py          # Errores de dominio (p. ej. ProductNotFoundError)
        ports.py                # Interfaces abstractas de repositorio (el "puerto")
    application/
        services.py              # Casos de uso; solo dependen de los ports
    infrastructure/
        repositories.py           # Adaptador concreto que implementa el port con el ORM
    api/
        serializers.py             # Adaptador de entrada/salida HTTP (DRF)
        views.py                    # Adaptador HTTP (DRF APIView)
        urls.py
    tests.py
```

## Capas

### 1. Dominio (`domain/`)
Entidades de negocio como dataclasses independientes de cualquier framework (`User`, `Product`, `Order`), excepciones de dominio y los *ports*: interfaces abstractas (`abc.ABC`) que declaran qué necesita el caso de uso de la persistencia, sin saber cómo se implementa.

### 2. Aplicación (`application/`)
Contiene los casos de uso (`AuthenticationService`, `CatalogService`, `OrderService`). Dependen únicamente de los ports del dominio — nunca importan Django ORM ni DRF directamente. `OrderService.create_order` envuelve la validación de stock, el cálculo del total y la persistencia dentro de `transaction.atomic()`, garantizando consistencia transaccional real (RF-03.3).

### 3. Infraestructura (`infrastructure/` + `models.py`)
Adaptadores concretos que implementan los ports usando el ORM de Django (`DjangoUserRepository`, `DjangoProductRepository`, `DjangoOrderRepository`). Las consultas van parametrizadas por el ORM, eliminando por diseño el riesgo de inyección SQL.

### 4. Adaptadores HTTP (`api/`)
Vistas `APIView` de Django REST Framework que solo reciben la petición HTTP, validan la entrada con un serializer y delegan al caso de uso correspondiente instanciándolo con el repositorio concreto (inyección de dependencias manual, sin framework de DI):

```python
service = AuthenticationService(user_repository=DjangoUserRepository())
user = service.authenticate(**serializer.validated_data)
```

## Diagrama conceptual

```text
+----------------------------+
| HTTP / Django REST Framework|
| apps/<contexto>/api/        |
+---------------+--------------+
                |
                v
+----------------------------+
| Application (casos de uso)  |
| apps/<contexto>/application/ |
+---------------+--------------+
                |
                v
+----------------------------+
| Domain (entidades y ports)   |
| apps/<contexto>/domain/       |
+---------------+--------------+
                |
                v
+----------------------------+
| Infrastructure (adaptador ORM)|
| apps/<contexto>/infrastructure/|
+---------------+--------------+
                |
                v
+----------------------------+
| SQLite (Django ORM)          |
+----------------------------+
```

## Alcance de esta migración
Esta migración replica la funcionalidad existente (`/`, `/login`, `/create_order`, `/get_all_orders_legacy`) sobre Django, corrige el bug legado por el cual `/create_order` y `/get_all_orders_legacy` nunca se registraban en Flask (estaban declaradas después de `app.run()`), y mueve el `SECRET_KEY` a variables de entorno (`.env`, vía `django-environ`). **No** incluye todavía hashing de contraseñas, JWT, roles, PostgreSQL, Docker/Kubernetes, CI/CD ni observabilidad — esos siguen siendo el alcance de HU-02 en adelante.

## Beneficios
- Cada contexto (usuarios, catálogo, órdenes) puede evolucionar de forma independiente.
- Los casos de uso son testeables sin levantar Django ni base de datos real, sustituyendo el repositorio por un doble de prueba.
- Django REST Framework deja preparado el terreno para JWT (`djangorestframework-simplejwt`) y permisos por rol en las siguientes historias de usuario.
