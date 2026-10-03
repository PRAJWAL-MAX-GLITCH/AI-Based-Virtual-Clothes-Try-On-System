# AI-Based Virtual Clothes Try-On System (Backend)

This is the backend for the AI-Based Virtual Clothes Try-On System, built with Flask.

## Architecture
- **App Factory Pattern**: The application is created via `app.create_app()`.
- **Blueprints**: Routes are modularized into blueprints (e.g., `health_bp`).
- **Configuration**: Uses `.env` for environment variables and class-based config.
- **Error Handling**: Centralized error responses mapping standard HTTP codes.
- **Extensions**: Scalable integration for CORS and future modules.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows)
3. Install requirements: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`
5. Ensure you have MongoDB installed and running locally, or use a MongoDB Atlas URI.
6. Set `MONGO_URI` in `.env` (e.g. `mongodb://localhost:27017/`)
7. Set `MONGO_DB_NAME` in `.env` (e.g. `virtual_try_on`)
8. Run the app: `python run.py`

## Testing
Run tests using pytest:
`pytest`

To test the health APIs manually:
- API Health: `GET http://127.0.0.1:5000/api/v1/health`
- DB Health: `GET http://127.0.0.1:5000/api/v1/health/db`

## Authentication API Tests (Postman / Thunder Client)
1. **Register**: `POST /api/v1/auth/register`
   - JSON Body: `{"name": "Test User", "email": "test@example.com", "password": "StrongPassword123"}`
2. **Login**: `POST /api/v1/auth/login`
   - JSON Body: `{"email": "test@example.com", "password": "StrongPassword123"}`
   - *Copy the `access_token` from the response.*
3. **Current User (Protected)**: `GET /api/v1/auth/me`
   - Header: `Authorization: Bearer <your_token>`

## User Management APIs (Protected, require Bearer token)
1. **Get Profile**: `GET /api/v1/users/me`
2. **Update Profile**: `PUT /api/v1/users/me`
   - JSON Body: `{"name": "New Name", "email": "new@example.com"}`
3. **Change Password**: `PATCH /api/v1/users/me/password`
   - JSON Body: `{"current_password": "Old", "new_password": "New"}`
4. **Deactivate Account**: `DELETE /api/v1/users/me`
   - *Sets `is_active=False`*

## Clothing Catalog APIs
*Require Bearer token.*

1. **List Clothing**: `GET /api/v1/clothing`
   - Supports query params: `?category=t-shirt`, `?search=black`, `?color=black`, `?available=true`, `?page=1`, `?limit=12`, `?sort=price_asc`
2. **Get Single Clothing**: `GET /api/v1/clothing/<clothing_id>/preview` - Preview catalog image

### Try-On History API

- `GET /api/v1/history` - Retrieve paginated try-on history for the authenticated user (supports `?page=1&limit=20`)
- `GET /api/v1/history/<history_id>` - Retrieve a specific history record
- `DELETE /api/v1/history/<history_id>` - Delete a history record and its associated generated result image
- `GET /api/v1/history/<history_id>/result` - Securely fetch the actual generated try-on image for a history record

## Security & Architecture
*Admin-Only (Require token from an account with `role: "admin"`):*
3. **Create Clothing**: `POST /api/v1/clothing`
   - JSON Body: `{"name": "...", "category": "t-shirt", "price": 799, "color": "black", "sizes": ["M", "L"]}`
4. **Update Clothing**: `PUT /api/v1/clothing/<id>`
   - JSON Body: Updates any fields above.
5. **Deactivate Clothing**: `DELETE /api/v1/clothing/<id>`
   - *Sets `available=False` rather than permanent deletion.*

*Supported categories: `t-shirt, shirt, hoodie, jacket, dress, top`*

*Note: Roles are defaulted to `user`. Admin routes are protected via `@admin_required()`. JWT tokens are stateless; expiration is handled via the `JWT_ACCESS_TOKEN_EXPIRES` env variable.*

---

## 🔒 Security Model (Prompt 14 Hardening)

### Authentication
- JWT tokens are **stateless** and signed with `JWT_SECRET_KEY` from environment (never hardcoded).
- Missing, malformed, or expired tokens receive a `401` with a safe generic error code.
- Inactive users (`is_active=false`) are rejected at the decorator level with `403 ACCOUNT_INACTIVE`.

### Authorization
- Role (`user` vs `admin`) is always read from the **database**, never from the request body.
- A normal user sending `{"role": "admin"}` in any request body will have it silently ignored.
- `@admin_required()` checks the role from the DB-fetched user object, not the token payload.

### User Ownership / IDOR Protection
- Every private resource lookup enforces `user_id = current_user.id` in the **MongoDB query**, not in application code after the fact.
- Examples:
  - `GET /api/v1/user-clothing/<id>` → queries `{_id: ..., user_id: current_user_id}`
  - `GET /api/v1/history/<id>` → queries `{_id: ..., user_id: current_user_id}`
  - `POST /api/v1/tryon` → validates person image and custom clothing ownership before processing
- A 404 is returned (never 403) for ownership mismatches to avoid confirming resource existence.

### Profile Update Security
- `PUT /api/v1/users/me` only allows `name` and `email` changes.
- Fields `role`, `_id`, `password_hash`, `is_active`, `created_at`, `updated_at` are **hardcoded blocked** in `user_service.update_user_profile`.

### Password Security
- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2/SHA-256) — never stored in plain text.
- `password_hash` is never returned in any API response (`serialize_user` strips it).
- Passwords and tokens are never written to application logs.

### File Upload Security
- Only `JPG`, `JPEG`, `PNG`, `WEBP` are accepted (enforced by both extension and Pillow decode validation).
- Empty and corrupted images are rejected before writing to disk.
- Filenames are regenerated as `UUID4` hex strings; the original client filename is discarded.
- Maximum upload size is enforced by Flask's `MAX_CONTENT_LENGTH` (default 5MB).

### Path Traversal Protection
- `GET /api/v1/static/<path>` normalizes the resolved path and verifies it is within `UPLOAD_FOLDER` before serving. Any `../` traversal attempts receive `403`.
- `save_image()` in `image_utils.py` has the same normpath guard.
- The `history_service.delete_history` verifies the result path starts with `results/` before deletion.

### Static File Access Control
- `/api/v1/static/<path>` requires a valid JWT (`@jwt_required()`).
- `results/<...>` paths are verified against a `tryon_history` ownership query before being served.
- Catalog images are accessible to any authenticated user.

### MongoDB Query Safety
- `get_clothing_list` whitelists allowed filter fields (`category`, `color`, `available`, `search`, `sort`) and validates types before passing to MongoDB. Raw request data is **never** passed directly to `.find()`.
- All ObjectId inputs are validated before use (`try: ObjectId(...)` / `except InvalidId`).
- Pagination values are clamped to safe ranges.

### Global Error Handling
- `app/utils/error_handlers.py` registers handlers for `AppError`, `HTTPException`, `RequestEntityTooLarge`, `NotFound`, `Forbidden`, `MethodNotAllowed`, and the catch-all `Exception`.
- **No stack traces, Python tracebacks, or internal paths are ever returned to clients.**
- All unexpected exceptions are logged server-side with `exc_info=True` for debugging.

### Security Headers
- CORS origins are controlled via `CORS_ORIGINS` environment variable (defaults to `http://localhost:3000`).
- `X-Content-Type-Options`, `X-Frame-Options` should be added via a reverse proxy (nginx) in production.

### Configuration & Secrets
- All secrets (`JWT_SECRET_KEY`, `MONGO_URI`, etc.) come from environment variables via `.env`.
- `.env` is in `.gitignore`. `.env.example` contains only placeholder values.
- `DEBUG` defaults to `False` (only enabled when `FLASK_DEBUG=1` is explicitly set).

### Known Limitations
- This is a **development backend**. For production, add:
  - Rate limiting on auth endpoints (e.g., Flask-Limiter)
  - HTTPS / TLS termination (nginx or a reverse proxy)
  - HTTP security headers (`Strict-Transport-Security`, `Content-Security-Policy`)
  - Centralized log aggregation (never log to plaintext files in production)
- File serving via `/api/v1/static/` is suitable for development. Production should use cloud storage (S3, GCS) with signed URLs.

