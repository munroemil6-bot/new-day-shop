from pathlib import Path

from flask import flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_
from app.models import MIN_PASSWORD_LENGTH, db, Item, Purchase, User

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'
DIST_DIR = FRONTEND_DIR / 'dist'


def serve_frontend():
    index_path = DIST_DIR / 'index.html'
    if index_path.exists():
        return send_from_directory(DIST_DIR, 'index.html')
    return send_from_directory(FRONTEND_DIR, 'index.html')


def register_routes(app):
    def error_response(message, status=400):
        return jsonify({'error': message}), status

    @app.route('/', methods=['GET'])
    def index():
        return serve_frontend()

    @app.route('/assets/<path:filename>')
    def assets(filename):
        return send_from_directory(DIST_DIR / 'assets', filename)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip().lower()
            password = request.form.get('password') or ''

            if not username or not email or not password:
                flash('Username, email, and password are required.', 'danger')
                return render_template('signup.html')

            if len(password) < MIN_PASSWORD_LENGTH:
                flash(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.', 'danger')
                return render_template('signup.html')

            existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()
            if existing_user:
                flash('A user with that username or email already exists.', 'danger')
                return render_template('signup.html')

            user = User(username=username, email=email)
            try:
                user.set_password(password)
            except ValueError as exc:
                flash(str(exc), 'danger')
                return render_template('signup.html')

            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully.', 'success')
            return redirect(url_for('shop'))

        return render_template('signup.html')

    @app.route('/login', methods=['GET'])
    def login():
        return serve_frontend()

    @app.route('/login', methods=['POST'])
    def login_post():
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('shop'))

        flash('Invalid username or password.', 'danger')
        return render_template('login.html')

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        if current_user.is_authenticated:
            logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/shop', methods=['GET'])
    def shop():
        return serve_frontend()

    @app.route('/purchase-history', methods=['GET'])
    @login_required
    def purchase_history():
        return serve_frontend()

    @app.route('/buy/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    def buy_item(item_id):
        item = Item.query.get_or_404(item_id)
        if request.method == 'POST':
            quantity = int(request.form.get('quantity', 1))
            if item.stock < quantity:
                flash('Not enough stock available.', 'danger')
                return render_template('buy_item.html', item=item)

            total_price = item.price * quantity
            purchase = Purchase(
                user_id=current_user.id,
                item_id=item.id,
                quantity=quantity,
                total_price=total_price,
            )
            item.stock -= quantity
            db.session.add(purchase)
            db.session.commit()
            flash('Purchase completed successfully.', 'success')
            return redirect(url_for('purchase_history'))

        return render_template('buy_item.html', item=item)

    @app.route('/api/auth/signup', methods=['POST'])
    def api_signup():
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not username or not email or not password:
            return error_response('Username, email, and password are required.', 400)

        if len(password) < MIN_PASSWORD_LENGTH:
            return error_response(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.', 400)

        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()
        if existing_user:
            return error_response('A user with that username or email already exists.', 400)

        user = User(username=username, email=email)
        try:
            user.set_password(password)
        except ValueError as exc:
            return error_response(str(exc), 400)

        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 201

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return error_response('Username and password are required.', 400)

        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        if not user or not user.check_password(password):
            return error_response('Invalid username or password.', 401)

        login_user(user)
        return jsonify(user.to_dict())

    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def api_logout():
        logout_user()
        return jsonify({'message': 'Successfully logged out.'})

    @app.route('/api/auth/user', methods=['GET'])
    def api_current_user():
        if not current_user.is_authenticated:
            return error_response('Not authenticated.', 401)

        return jsonify(current_user.to_dict())

    @app.route('/api/items', methods=['GET', 'POST'])
    def api_items():
        if request.method == 'GET':
            items = Item.query.order_by(Item.name).all()
            return jsonify([item.to_dict() for item in items])

        if not current_user.is_authenticated:
            return error_response('Authentication required for item creation.', 401)

        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        price = data.get('price')
        stock = data.get('stock')

        if not name or price is None or stock is None:
            return error_response('Item name, price, and stock are required.', 400)

        item = Item(
            name=name,
            description=data.get('description', '').strip(),
            price=float(price),
            stock=int(stock),
        )
        db.session.add(item)
        db.session.commit()

        return jsonify(item.to_dict()), 201

    @app.route('/api/items/<int:item_id>', methods=['GET'])
    def api_item(item_id):
        item = Item.query.get_or_404(item_id)
        return jsonify(item.to_dict())

    @app.route('/api/purchases', methods=['GET', 'POST'])
    @login_required
    def api_purchases():
        if request.method == 'GET':
            purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.purchased_at.desc()).all()
            return jsonify([purchase.to_dict() for purchase in purchases])

        data = request.get_json() or {}
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        if item_id is None or quantity is None:
            return error_response('Item ID and quantity are required.', 400)

        item = Item.query.get(item_id)
        if not item:
            return error_response('Item not found.', 404)

        quantity = int(quantity)
        if quantity < 1:
            return error_response('Quantity must be at least 1.', 400)

        if item.stock < quantity:
            return error_response('Not enough stock available.', 400)

        total_price = item.price * quantity
        purchase = Purchase(
            user_id=current_user.id,
            item_id=item.id,
            quantity=quantity,
            total_price=total_price,
        )
        item.stock -= quantity
        db.session.add(purchase)
        db.session.commit()

        return jsonify(purchase.to_dict()), 201
