# Backend (Django)

## Run locally
1. Create venv and install:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Set env vars (use .env.example values):
```
set DJANGO_SECRET_KEY=dev
set DEBUG=true
set DB_NAME=myshopdb
set DB_USER=myshopuser
set DB_PASSWORD=mypassword
set DB_HOST=localhost
```
3. Run migrations and server:
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Deploy on Render
- Use `python 3.11`, build command:
```
pip install -r backend/requirements.txt
python backend/manage.py migrate
```
- Start command:
```
python backend/manage.py collectstatic --noinput && gunicorn ecom.wsgi
```
- Environment Variables:
  - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST (from your Render PostgreSQL)
  - DJANGO_SECRET_KEY
  - DEBUG=false

## Endpoints (changed)
- Auth:
  - POST /api/accounts/signup/
  - GET /api/accounts/me/  (requires auth)
  - GET /api/accounts/vendors/
- Shops:
  - GET /api/shop/shops/
  - GET /api/shop/shops/my_shop/
  - POST /api/shop/shops/my_shop/update/
- Products:
  - GET /api/shop/products/
  - GET /api/shop/products/?vendor=<id>
  - GET /api/shop/products/my_products/
  - POST /api/shop/products/create/
  - POST /api/shop/products/<id>/import_to_my_shop/
- Orders:
  - POST /api/shop/orders/ (guest checkout allowed)
  - GET /api/shop/orders/list/ (vendor/dropshipper)
  - PATCH /api/shop/orders/<id>/ (vendor can update status)