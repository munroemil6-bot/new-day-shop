# Flask + React Shop

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

## Add items from the Flask shell

```bash
pipenv run flask shell
```

```python
from app import create_app
from app.models import db, Item
app = create_app()
with app.app_context():
    i = Item(name='Maize Flour', description='2 kg pack of white maize flour', price=240.0, stock=12)
    db.session.add(i)
    db.session.commit()
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
