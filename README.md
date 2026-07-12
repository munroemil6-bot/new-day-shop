# newdy shop

This project runs as a Flask app that serves the built React frontend from the backend.

## Backend

- `run.py`: starts the Flask backend on `http://localhost:5000`
- `app/`: Flask application package
- `app/routes.py`: serves the frontend and exposes the API endpoints

## Frontend

- `frontend/`: React + Vite frontend source
- `frontend/package.json`: React and Vite dependencies
- `frontend/vite.config.js`: local dev proxy settings

## Local setup

1. Install backend dependencies:

```bash
pipenv install
```

2. Build the frontend assets:

```bash
cd frontend
npm install
npm run build
cd ..
```

3. Start the Flask backend:

```bash
pipenv run python run.py
```

4. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Run on a different port

If port 5000 is busy, run:

```bash
FLASK_RUN_PORT=8000 pipenv run python run.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Create users from the Flask shell

You can create users directly from the Flask shell:

```bash
pipenv run flask shell
```

```python
from app import create_app
from app.models import db, User
app = create_app()
with app.app_context():
    u = User(username='naomi', email='naomi@gmail.com')
    u.set_password('12345')
    db.session.add(u)
    db.session.commit()
```

For a single user in one line before add/commit:

```python
u = User(username='naomi', email='naomi@gmail.com'); u.set_password('12345'); db.session.add(u); db.session.commit()
```

## Flask Shell Commands

Enter the Flask shell:

```bash
pipenv run flask shell
```

### Setup (one-time in shell)

```python
from app import create_app
from app.models import db, User, Item, Purchase
app = create_app()
app.app_context().push()
```

### Add Items to Shop

```python
# Single item
i = Item(name='Maize Flour', description='2 kg pack of white maize flour', price=240.0, stock=12)
db.session.add(i)
db.session.commit()

# Multiple items at once
items = [
    Item(name='Rice', description='1 kg white rice', price=150.0, stock=20),
    Item(name='Beans', description='1 kg dried beans', price=120.0, stock=15),
    Item(name='Sugar', description='2 kg sugar pack', price=200.0, stock=25)
]
db.session.add_all(items)
db.session.commit()
```

### View All Items

```python
# List all items
items = Item.query.all()
for item in items:
    print(f"ID: {item.id}, Name: {item.name}, Price: {item.price}, Stock: {item.stock}")

# Find item by ID
item = Item.query.get(1)
print(item.name, item.price)

# Find item by name
item = Item.query.filter_by(name='Maize Flour').first()
```

### Edit/Update Items in Shop

```python
# Update item by ID
item = Item.query.get(1)
item.name = 'Premium Maize Flour'
item.price = 250.0
item.stock = 15
db.session.commit()

# Update stock for multiple items
Item.query.filter_by(name='Rice').update({'stock': 30})
db.session.commit()
```

### Delete Items from Shop

```python
# Delete single item by ID
item = Item.query.get(1)
db.session.delete(item)
db.session.commit()

# Delete item by name
item = Item.query.filter_by(name='Rice').first()
db.session.delete(item)
db.session.commit()

# Delete all items from a query
items = Item.query.filter(Item.price > 500).all()
for item in items:
    db.session.delete(item)
db.session.commit()
```

### Add Purchases to User (User Buys Item)

```python
# User purchases an item
user = User.query.filter_by(username='naomi').first()
item = Item.query.filter_by(name='Maize Flour').first()

purchase = Purchase(user_id=user.id, item_id=item.id, quantity=2, total_price=item.price * 2)
db.session.add(purchase)
db.session.commit()

# Add multiple purchases
purchases = [
    Purchase(user_id=1, item_id=1, quantity=1, total_price=240.0),
    Purchase(user_id=1, item_id=2, quantity=3, total_price=450.0)
]
db.session.add_all(purchases)
db.session.commit()
```

### View User Purchases

```python
# Get all purchases for a user
user = User.query.filter_by(username='naomi').first()
purchases = user.purchases
for purchase in purchases:
    print(f"Item: {purchase.item.name}, Qty: {purchase.quantity}, Total: {purchase.total_price}")

# Get purchase by ID
purchase = Purchase.query.get(1)
print(f"User: {purchase.user.username}, Item: {purchase.item.name}")

# List all purchases
all_purchases = Purchase.query.all()
```

### Delete Purchases

```python
# Delete single purchase by ID
purchase = Purchase.query.get(1)
db.session.delete(purchase)
db.session.commit()

# Delete all purchases for a user
user = User.query.filter_by(username='naomi').first()
Purchase.query.filter_by(user_id=user.id).delete()
db.session.commit()

# Delete all purchases of a specific item
Purchase.query.filter_by(item_id=1).delete()
db.session.commit()
```

### Delete Users

```python
# Delete user by username
user = User.query.filter_by(username='naomi').first()
db.session.delete(user)
db.session.commit()

# Delete user by ID
user = User.query.get(1)
db.session.delete(user)
db.session.commit()
```

### View All Users

```python
# List all users
users = User.query.all()
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

# Find user by username
user = User.query.filter_by(username='naomi').first()

# Find user by email
user = User.query.filter_by(email='naomi@gmail.com').first()
```

### Quick Reference - One-Liners

```python
# Add item
Item.query.session.add(Item(name='Wheat', price=300.0, stock=10)) or db.session.commit()

# Update item stock
Item.query.get(1).stock = 50; db.session.commit()

# Delete item
Item.query.get(1) and db.session.delete(Item.query.get(1)) or db.session.commit()

# Count total items in shop
print(Item.query.count())

# Count total users
print(User.query.count())

# Total purchases made
print(Purchase.query.count())
```

For a single item in one line before add/commit:

```python
i = Item(name='Maize Flour', description='2 kg pack of white maize flour', price=240.0, stock=12); db.session.add(i); db.session.commit()
```

## Deployment notes

- This app is meant to be started with Flask directly for local development.
- For deployment, make sure the environment has the Flask dependencies installed and the frontend has been built with `npm run build`.
- The React frontend is configured to use a production API base URL from `VITE_API_BASE_URL`.
- If your host uses a different port, set it explicitly, for example:

```bash
FLASK_RUN_PORT=8000 pipenv run python run.py
```

### Deploying backend as a container image

1. Build a Docker image for the Flask backend.
2. Push it to a registry such as Docker Hub.
3. Deploy the image to a container host like Render, Fly, DigitalOcean App Platform, or AWS.

The frontend can then point at the public backend URL using `VITE_API_BASE_URL`.

### Deploying the frontend separately

- Build the React app with `npm run build`.
- Deploy the `frontend/dist` folder to static hosting such as Netlify, Vercel, or an S3-compatible host.
- Set `VITE_API_BASE_URL` to the backend URL you deployed.

## Notes

- The backend exposes JSON API routes under `/api/*`.
- The frontend can be served by Flask or hosted separately, as long as it is configured to call the backend URL.
