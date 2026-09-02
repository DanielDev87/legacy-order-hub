# Bitácora de Deuda Técnica (Ingeniería Inversa Asistida por IA)

> Documento generado mediante ingeniería inversa del código legado real de Legacy OrderHub, recuperado del historial de git (commits `cab8d4e`, `4c79d1d`, `58a584c`, previos a la migración a Django). Se actualiza cada vez que el proyecto sufre un cambio arquitectónico relevante.

---

## 1. Inyección SQL en `/login` (Crítico)

**Ubicación original:** `app.py` @ `4c79d1d` (versión inicial del legado).

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
print(f"[LOG LEGADO]: Ejecutando consulta SQL sin sanitizar: {query}")
user = cursor.execute(query).fetchone()
```

La consulta se construía concatenando directamente el `username`/`password` recibidos del cliente. Un payload como `' OR '1'='1' -- ` en `username` permitía autenticarse sin conocer ninguna contraseña, o exfiltrar datos vía `UNION SELECT`. El propio log imprimía la consulta cruda en consola, agravando la exposición.

**Estado:** ya remediado antes de esta entrega (commit `58a584c` introdujo `repositories/user_repository.py` con consultas parametrizadas `?`) y confirmado en la migración a Django: `apps/users/infrastructure/repositories.py` usa el ORM de Django (`UserModel.objects.filter(username=username)`), que parametriza toda consulta por diseño — no queda ninguna ruta de construcción manual de SQL en el proyecto.

## 2. Contraseñas almacenadas en texto plano (Crítico)

**Ubicación original:** `database.py` @ `4c79d1d` / `58a584c`.

```python
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
```

Las contraseñas se guardaban y comparaban tal cual, sin ningún hashing. Cualquier acceso de lectura a la base de datos (backup, dump, o la propia inyección SQL del punto 1) exponía las credenciales de todos los usuarios directamente.

**Estado:** remediado en esta entrega (RF-01.2). `apps/users/models.py` extiende `AbstractBaseUser` de Django; el campo `password` se gestiona con `set_password()`/`check_password()`. `PASSWORD_HASHERS` en `config/settings.py` prioriza `Argon2PasswordHasher`. El seed de datos (`apps/users/migrations/0002_seed_data.py`) hashea con `django.contrib.auth.hashers.make_password` antes de insertar — no existe ninguna ruta que persista una contraseña sin hashear.

## 3. Secretos y configuración hardcoded en el repositorio (Alto)

**Ubicación original:** `config.py` @ `4c79d1d`.

```python
SECRET_KEY = "clave_secreta_super_insegura_123"
DB_PASS = "admin1234_super_secret"
```

`SECRET_KEY` (usado por Flask para firmar sesiones/cookies) y credenciales de una base de datos que ni siquiera se usaba (`DB_HOST`/`DB_USER`/`DB_PASS`/`DB_NAME` — el proyecto solo usaba SQLite local) quedaban committeados en texto plano en el repositorio.

**Estado:** remediado en la migración a Django. `config/settings.py` lee `SECRET_KEY` desde una variable de entorno vía `django-environ` (`env('DJANGO_SECRET_KEY')`), cargada desde un `.env` que está en `.gitignore`. Se eliminaron las variables `DB_*` no usadas. Se commitea únicamente `.env.example` con valores placeholder.

## 4. Endpoints muertos por un bug de orden de declaración (Medio)

**Ubicación original:** `app.py` @ `58a584c` (justo antes de la migración a Django).

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/create_order', methods=['POST'])
def create_order():
    ...
```

Las rutas `/create_order` y `/get_all_orders_legacy` estaban declaradas **después** de la llamada bloqueante a `app.run()`, por lo que Flask nunca las registraba al ejecutar el script directamente — el código era alcanzable solo en teoría (p. ej. bajo un test client que importa el módulo sin ejecutar `__main__`), nunca en producción real. Además, ambas rutas llamaban a `get_db_connection()` sin importarlo en `app.py`, lo que habría lanzado `NameError` de haberse alcanzado.

**Estado:** remediado en la migración a Django. `apps/orders/api/views.py` (`CreateOrderView`, `OrderListView`) registra ambas rutas correctamente vía `apps/orders/api/urls.py`, verificado con pruebas de integración (`apps/orders/tests.py`) y una prueba manual end-to-end contra el servidor real.

## 5. Ausencia total de control de acceso por rol (Alto)

**Ubicación original:** ninguna — el legado no tenía ningún concepto de sesión autenticada ni de roles; cualquier cliente podía invocar cualquier endpoint sin restricción.

**Estado:** parcialmente remediado en esta entrega (RF-01.3, RF-01.4). `/login` emite un par de tokens JWT (`djangorestframework-simplejwt`) con expiración (`access`: 15 min, `refresh`: 1 día). La creación de productos (`POST /products`) exige un token válido y rol `admin` (`common/api/permissions.py::IsAdminRole`). El resto de endpoints (`/create_order`, `/get_all_orders_legacy`) permanece público de forma deliberada — está fuera del alcance de RF-01.4, que solo pide restringir operaciones administrativas como la creación de productos.

## 6. Ausencia de pruebas y de análisis estático (Alto)

**Ubicación original:** el legado no tenía ningún archivo de test funcional (solo un stub vacío) ni configuración de linters.

**Estado:** parcialmente remediado en esta entrega (RNF-01.2, RNF-01.3). Cobertura de pruebas actual ≥80% (`coverage run manage.py test` + `coverage report --fail-under=80`), verificado con `flake8`/`black` sin advertencias. Pendiente para entregas futuras: SAST dedicado (`bandit`), pipeline de CI (HU-05).
