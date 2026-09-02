# Arquitectura del Sistema (C4) — Legacy OrderHub

> Diagramas C4 obtenidos por ingeniería inversa asistida por IA: Nivel 1 (Contexto) y Nivel 2 (Contenedores), tanto del sistema legado (Flask, previo a esta entrega) como del estado actual (Django + DRF, arquitectura hexagonal). Se actualiza en cada cambio arquitectónico relevante — ver también [`HEXAGONAL_ARCHITECTURE.md`](HEXAGONAL_ARCHITECTURE.md) para el detalle de capas y [`TECHNICAL_DEBT_LOG.md`](TECHNICAL_DEBT_LOG.md) para la deuda técnica identificada.

---

## Estado actual (Django + DRF)

### C4 Nivel 1 — Contexto del sistema

```mermaid
C4Context
    title Legacy OrderHub — Contexto del sistema (actual)

    Person(cliente, "Usuario cliente", "Consulta el dashboard, inicia sesión, crea órdenes")
    Person(admin, "Usuario admin", "Además del uso normal, crea productos en el catálogo")

    System(orderhub, "Legacy OrderHub", "Django + DRF. Gestiona usuarios, catálogo de productos y órdenes de compra")

    System_Ext(navegador, "Navegador / Cliente HTTP", "Dashboard estático o llamadas directas a la API (curl, Postman, etc.)")

    Rel(cliente, navegador, "Usa")
    Rel(admin, navegador, "Usa")
    Rel(navegador, orderhub, "HTTP/JSON (login, crear orden, listar órdenes, crear producto)")
```

### C4 Nivel 2 — Contenedores

```mermaid
C4Container
    title Legacy OrderHub — Contenedores (actual)

    Person(usuario, "Usuario (cliente o admin)")

    System_Boundary(orderhub, "Legacy OrderHub") {
        Container(dashboard, "Dashboard", "Django Template + JS", "Panel de monitoreo visual servido en '/'")
        Container(api, "API REST", "Django REST Framework", "Expone /login, /token/refresh, /create_order, /get_all_orders_legacy, /products")
        ContainerDb(db, "Base de datos", "SQLite (dev)", "Tablas users, products, orders")
    }

    Rel(usuario, dashboard, "Consulta", "HTTPS")
    Rel(usuario, api, "Login / operaciones", "HTTPS + JWT Bearer")
    Rel(dashboard, api, "fetch()", "HTTP/JSON")
    Rel(api, db, "Lee/Escribe", "Django ORM")
```

Cada uno de los tres contextos delimitados (`apps/users`, `apps/catalog`, `apps/orders`) implementa internamente arquitectura hexagonal (dominio → aplicación → infraestructura → adaptador HTTP) — ver [`HEXAGONAL_ARCHITECTURE.md`](HEXAGONAL_ARCHITECTURE.md) para el desglose de capas.

---

## Sistema legado (Flask, previo a la migración)

Reconstruido a partir del historial de git (`git show 4c79d1d:app.py`), representa el estado del sistema antes de cualquier refactorización de esta asignatura.

### C4 Nivel 1 — Contexto del sistema (legado)

```mermaid
C4Context
    title Legacy OrderHub — Contexto del sistema (legado, pre-Django)

    Person(usuario, "Usuario", "Sin distinción de roles: cualquiera podía ejecutar cualquier operación")

    System(orderhub_legacy, "Legacy OrderHub v1.0", "Monolito Flask + SQLite, sin capas ni autenticación real")

    System_Ext(navegador, "Navegador / Cliente HTTP")

    Rel(usuario, navegador, "Usa")
    Rel(navegador, orderhub_legacy, "HTTP/JSON, sin autenticación")
```

### C4 Nivel 2 — Contenedores (legado)

```mermaid
C4Container
    title Legacy OrderHub — Contenedores (legado, pre-Django)

    Person(usuario, "Usuario")

    System_Boundary(orderhub_legacy, "Legacy OrderHub v1.0") {
        Container(app_py, "app.py", "Flask", "Todas las rutas y la lógica de negocio mezcladas en un único módulo")
        ContainerDb(sqlite, "orderhub.db", "SQLite", "Acceso vía SQL crudo, sin ORM")
    }

    Rel(usuario, app_py, "HTTP/JSON (login vulnerable a SQLi, create_order, get_all_orders_legacy)")
    Rel(app_py, sqlite, "Consultas SQL concatenadas con f-strings (login) o parametrizadas (resto)")
```

**Hallazgos clave de esta reconstrucción** (detalle completo en `TECHNICAL_DEBT_LOG.md`): inyección SQL real en `/login` vía f-string, contraseñas en texto plano, secretos hardcoded en `config.py`, y dos endpoints (`/create_order`, `/get_all_orders_legacy`) que nunca se registraban en tiempo de ejecución por estar declarados después de la llamada bloqueante a `app.run()`.
