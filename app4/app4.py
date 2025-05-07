from flask import Flask, render_template, request, jsonify, make_response, redirect, session, url_for, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, EmailField, PasswordField
from wtforms.validators import NumberRange, DataRequired, Regexp, ValidationError, Email, Length, EqualTo
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.hybrid import hybrid_property
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required

app = Flask(__name__)
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "ben should eat glass for dinner"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

class open_cafe(db.Model):
    __tablename__ = 'cafe_menu'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String(16), index = True, unique = True, nullable = False)
    price = db.Column (db.Float, nullable = False)
    description = db.Column(db.String)
    image  = db.Column(db.String)

#Maybe create a page that allows the user to buy the items and then displays all the pictures in a fun way to represent the items bought.It then resets the basket

# Want to create a basket for each user where user can add items and amount. Add constraints to the amount they can add, if item already exists then just increment the value there 
class basket(db.Model):
    __tablename__ = 'user_basket'
    id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column (db.Integer, db.ForeignKey('cafe_menu.id')) 
    item_quantity = db.Column (db.Integer, nullable = False)
    session_id = db.Column(db.Integer, db.ForeignKey('user_cookies_session.id'))
    item = db.relationship('open_cafe', backref = 'baskets')
    
    @hybrid_property
    def item_total_price(self):
        return round(self.item_quantity * self.item.price, 2)
    

# Want to create a login page, or a sign up page
# Each user has a unique id, name, password and basket_id
# Options to view the user account at all times, reset password?, delete account, try emailing for code?


class recipe (db.Model):
    __tablename__ = 'all_recipes'
    id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column (db.Integer, db.ForeignKey('cafe_menu.id'))
    ingredients = db.relationship('ingredient_recipe_amount', back_populates = 'recipe')

    @hybrid_property
    def total_carbon_footprint(self):
        total = 0
        for ingredient_recipe in self.ingredients:
            total += ingredient_recipe.amount * ingredient_recipe.ingredient.carbon_footprint
        return total


class ingredients (db.Model):
    __tablename__ = 'all_ingredients'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    carbon_footprint = db.Column (db.Integer)
    ingredient_recipe_amounts = db.relationship('ingredient_recipe_amount', back_populates='ingredient') 

class ingredient_recipe_amount(db.Model):
    __tablename__ = 'ingredients_for_each_recipe'
    id = db.Column (db.Integer, primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey ('all_recipes.id'))
    ingredient_id = db.Column (db.Integer, db.ForeignKey ('all_ingredients.id'))
    amount = db.Column (db.Float)
    recipe = db.relationship('recipe', back_populates = 'ingredients')
    ingredient = db.relationship('ingredients', back_populates = 'ingredient_recipe_amounts')


# One user multiple user sessions. Allow users to create multiple user sessions? Multiple baskets? Show history of purchases?
class user_session(db.Model):
    __tablename__ = 'user_cookies_session'
    id = db.Column (db.Integer, primary_key = True)
    cookie = db.Column (db.String(100), unique = True, nullable = False)
    creation_time = db.Column (db.DateTime, default = datetime.utcnow)
    user_id = db.Column (db.Integer, db.ForeignKey('user_information.id'), nullable = True)

    session_basket = db.relationship('basket', backref = 'session', lazy = True)

    @hybrid_property
    def total_basket_price(self):
        return round(sum(item.item_total_price for item in self.session_basket), 2)

class user(db.Model):
    __tablename__ = 'user_information'
    id = db.Column (db.Integer, primary_key = True)
    name = db.Column (db.String, nullable = False)
    email = db.Column (db.String(256), unique = True, nullable = False)
    username = db.Column (db.String(34), unique = True, nullable = False)
    password_hash = db.Column ('password', db.String(128), nullable = False)
    # I want to store user's credit card information so user can use a previously saved card
    session = db.relationship('user_session', backref = 'user', lazy = True, uselist = False)

    @hybrid_property
    def password(self):
        return self.password_hash
    
    @password.setter
    def password(self, user_password):
        self.password_hash = generate_password_hash(user_password)

    def check_password(self, password_entry):
        return check_password_hash(self.password_hash, password_entry)
    
class purchase_history(db.Model):
    __tablename__ = 'user_purchase_history'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column (db.Integer, db.ForeignKey('user_information.id'), nullable = False)
    session_id = db.Column (db.Integer, db.ForeignKey('user_cookies_session.id'), nullable = False)
    purchase_time = db.Column(db.DateTime, default = datetime.utcnow)
    total_price = db.Column (db.Float, nullable = False)
    session = db.relationship('user_session', backref = 'purchases', lazy = True)
    user = db.relationship('user', backref = 'purchases', lazy = True)

    @hybrid_property
    def basket(self):
        return self.session.session_basket
    
class purchase_item(db.Model):
    __tablename__ = 'purchased_items'
    id = db.Column(db.Integer, primary_key = True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('user_purchase_history.id'), nullable = False)
    item_name = db.Column(db.String(100), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    total_price = db.Column(db.Float, nullable = False)

    purchase = db.relationship('purchase_history', backref='items', lazy=True)

class credit_card(db.Model):
    __tablename__ = 'user_credit_cards'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_information.id'), nullable = False)
    card_last4 = db.Column(db.String(4), nullable = False)
    card_token = db.Column(db.String(128), nullable = False) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Basket_form(FlaskForm):
    amount = IntegerField('Add the desired amount', validators = [DataRequired(), NumberRange(min = 1, max = 15)])
    buy = SubmitField('Buy')

class checkout_form(FlaskForm):
    login = SubmitField('Login')
    guest = SubmitField('Continue as a Guest')

class credit_card_form (FlaskForm):
    credit_card_number = StringField('Credit Card Number', validators = [
        DataRequired(), 
        Regexp(
            r'^[\d\s-]+$', 
            message = "Credit card number must consit of digits, spaces or dashes"
        )
    ], render_kw={"autocomplete" : "off"}
    )
    pay = SubmitField("Pay")

    def validate_credit_card_number(self, field):
        cleaned_number = field.data.replace(" ", "").replace("-", "")
        if not cleaned_number.isdigit() or len(cleaned_number) != 16:
            raise ValidationError("Credit card number must be exactly 16 digits.")
            
class login_or_create_form(FlaskForm):
    login = SubmitField('Login into existing account')
    create = SubmitField('Create a new account')

class create_account_form(FlaskForm):
    name = StringField('Enter your name', validators = [DataRequired()])
    email = EmailField('Enter your email', validators =[
        DataRequired(),
        Email('Please enter a valid email')
    ])
    #Username and email should not exist in the database
    username = StringField('Enter a username', validators = [DataRequired()])
    password = PasswordField('Enter a password', validators = [
        DataRequired(),
        Length(min = 8, max = 16)
    ])
    confirm_password = PasswordField('Confim Password', validators = [
        DataRequired(), 
        EqualTo('password', message = 'Passwords must match'), 
    ])
    submit = SubmitField('Create Account')


class login_form(FlaskForm):
    credentials = StringField('Enter your username or email', validators = [DataRequired()])
    password = PasswordField('Enter your password', validators = [
        DataRequired(), 
        Length(min = 8, max = 16)
    ])
    submit = SubmitField('Login')
    
class create_new_password_form(FlaskForm):
    old_password = PasswordField('Enter your old password', validators = [
        DataRequired(), 
        Length(min = 8, max = 16)
    ])
    new_password = PasswordField('Enter your new password', validators = [
        DataRequired(), 
        Length(min = 8, max = 16)
    ])
    confirm_password = PasswordField('Confim your new password', validators = [
        DataRequired(), 
        EqualTo('new_password', message = 'Passwords must match'), 
    ])
    submit = SubmitField('Create new password')



def create_session(cookie = None, user_account = None):
    if cookie is None:
        cookie = str(uuid.uuid4())
        new_cookie = True
        
    if user_account:
        current_user = user_account
    else:
        current_user = get_current_user()

    if  current_user:
        session = user_session(cookie = cookie, user_id = current_user.id)
    else:
        session = user_session(cookie = cookie)
    
    db.session.add(session)
    db.session.commit()

    if new_cookie:
        return session, cookie
    return session

def get_current_session():
    user_cookie = request.cookies.get('user_cookie')
    session = user_session.query.filter_by (cookie = user_cookie).first()
    return session

def get_current_user():
    session = get_current_session()
    if session and session.user_id:
        return user.query.filter_by(id = session.user_id).first()
    return None



@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return redirect('/')

@app.route('/')
def galleryPage():
    cafe_menu = open_cafe.query.all()
    cafe_recipes = recipe.query.all()
    csrf_token = generate_csrf()
    user_cookie = request.cookies.get('user_cookie')
    current_user = get_current_user()
    if not user_cookie:
        current_session, new_cookie = create_session()
        cookie_website = make_response(render_template('index.html',cafe_menu = cafe_menu, cafe_recipes = cafe_recipes, csrf_token = csrf_token, current_user = current_user))
        cookie_website.set_cookie('user_cookie', new_cookie, max_age = 60 * 60 * 24 * 30)
        return cookie_website
    
    current_session = get_current_session()
    if not current_session:
        current_session = create_session(user_cookie)

    return render_template('index.html',cafe_menu = cafe_menu, cafe_recipes = cafe_recipes, csrf_token = csrf_token, current_user = current_user)


@app.route('/product_page/<int:item>', methods = ['GET', 'POST'])
def singleProductPage(item):
    purchase_form = Basket_form()
    selected_item = open_cafe.query.get_or_404(item)
    current_session = get_current_session()
    current_user = get_current_user()

    if purchase_form.validate_on_submit():
        print("Form validated! Processing basket...")
        quantity = purchase_form.amount.data
        item_entry = basket.query.filter_by(item_id = selected_item.id, session_id = current_session.id).first()
        if item_entry:
            item_entry.item_quantity += quantity
        else:
            if(quantity > 0):
                item_entry = basket(item_id = selected_item.id, item_quantity = quantity, session_id = current_session.id)
                db.session.add(item_entry)

        db.session.commit()

        return render_template('PurchaseProduct.html', item=selected_item, quantity_added = quantity, basket_entry=item_entry, current_user = current_user) 
    else: 
        return render_template('SingleProduct.html', cafe_item = selected_item, basket = purchase_form, current_user = current_user)
    
# @app.route('user/basket')
@app.route('/basket')
def basketPage():
    session = get_current_session()
    current_user = get_current_user()
    user_login = False
    if session is None:
        print('No session')
        return redirect('/')
    user_basket = basket.query.filter_by(session_id = session.id).all()
    csrf_token = generate_csrf()
    if current_user:
        user_login = True
    return render_template('ViewBasket.html', user_basket = user_basket, csrf_token = csrf_token, current_user = current_user, user_login = user_login)

@app.route('/payment', methods = ['GET', 'POST'])
def payment():
    session = get_current_session()
    user_basket = basket.query.filter_by(session_id = session.id).all()
    payment_form = credit_card_form()
    current_user = get_current_user()
    saved_cards = credit_card.query.filter_by(user_id = current_user.id).all() if current_user else []
    if request.method == 'POST':
        selected_card_id = request.form.get('saved_card_id')
        use_saved = selected_card_id and selected_card_id != 'new'

        if use_saved:
            card = credit_card.query.filter_by(id = selected_card_id, user_id = current_user.id).first()
            if card:
                print(f"Processing payment with saved card {card.card_last4}")
                return redirect('/checkout/complete')

        elif payment_form.validate():
            card_number = payment_form.credit_card_number.data
            last4 = card_number[-4:]
            token = "tok_" + str(uuid.uuid4())[:16]

            if current_user and request.form.get('save_card'):
                new_card = credit_card(user_id = current_user.id, card_last4=last4, card_token=token)
                db.session.add(new_card)
                db.session.commit()

            return redirect('/checkout/complete')

    return render_template('checkout.html', user_basket = user_basket, payment_form = payment_form, session = session, current_user = current_user, saved_cards = saved_cards)


@app.route('/checkout', methods = ['GET', 'POST'])
def checkout():
    checkout_choice_form = checkout_form()
    current_user = get_current_user()

    if checkout_choice_form.validate_on_submit():
        if checkout_choice_form.login.data:
            return redirect ('/login')
        else:
           return redirect('/payment')

    return render_template('checkout.html', choice_form = checkout_choice_form, current_user = current_user)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_choice = login_or_create_form()
    user_login_form = login_form()
    current_user = get_current_user()

    if login_choice.validate_on_submit():
        if login_choice.login.data:
            return render_template('login.html',login_or_create_form = None, user_login_form = user_login_form, current_user = current_user)
        elif login_choice.create.data:
            return redirect ('/create_account')
    if user_login_form.validate_on_submit():
        user_account = user.query.filter_by(username=user_login_form.credentials.data).first()
        if not user_account:
            user_account = user.query.filter_by(email=user_login_form.credentials.data).first()
            if not user_account:
                user_login_form.credentials.errors.append('Invalid Credentials')
                return render_template('login.html', login_or_create_form = None, user_login_form = user_login_form, current_user = current_user)
        if user_account.check_password(user_login_form.password.data):
            current_session = get_current_session()
            session['guest_cookie'] = request.cookies.get('user_cookie')
            if user_account.session:
                current_session = user_account.session
                new_cookie = user_account.session.cookie
            else:
                current_session, new_cookie = create_session(None, user_account)
                db.session.add(current_session)
                db.session.commit()
            print('Account found!')
            user_website = make_response(redirect('/'))
            user_website.set_cookie('user_cookie', new_cookie, max_age = 60 * 60 * 24 * 30)
            return user_website
        user_login_form.password.errors.append('Incorrect Password')
        return render_template('login.html', login_or_create_form = None, user_login_form = user_login_form, current_user = current_user)

    return render_template('login.html', login_or_create_form = login_choice, user_login_form = None, current_user = current_user)


#add delete account mechnaism, save credit card mechanism
@app.route('/create_account', methods = ['POST', 'GET'])
def create_account():
    create_form = create_account_form()
    csrf_token = generate_csrf()
    current_user = get_current_user()

    if create_form.validate_on_submit():
        error = False
        if user.query.filter_by(username = create_form.username.data).first():
            create_form.username.errors.append('Username already taken.')
            error = True
        if user.query.filter_by(email=create_form.email.data).first():
            create_form.email.errors.append('Email already registered.')
            error = True
        if not error:
            new_user = user(
                name = create_form.name.data,
                email = create_form.email.data,
                username = create_form.username.data,
                password = create_form.password.data  
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')    
        
    return render_template ('create_account.html', form = create_form, csrf_token = csrf_token, validation = False, current_user = current_user)

# Add item names to purchase history
@app.route('/checkout/complete')
def checkout_complete():
    current_user = get_current_user()
    current_session = get_current_session()
    if current_user:
        purchase_entry = purchase_history(user_id = current_session.user_id, session_id = current_session.id, total_price = current_session.total_basket_price )
        db.session.add(purchase_entry)
        db.session.flush()

        for item in current_session.session_basket:
            purchase_item_entry = purchase_item(
                purchase_id = purchase_entry.id,
                item_name = item.item.name,
                quantity = item.item_quantity,
                total_price = item.item_total_price
            )
            db.session.add(purchase_item_entry)

        db.session.commit()

    new_session, new_cookie = create_session()
    current_session = new_session
    user_website = make_response(render_template('checkout_complete.html', current_user = current_user))
    user_website.set_cookie('user_cookie', new_cookie, max_age = 60*60*24*30)
    return user_website



@app.route('/add_to_basket', methods = ['POST'])
def add_to_basket():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')
    session = get_current_session()

    item_entry = basket.query.filter_by(item_id = item_id, session_id = session.id).first()
    if item_entry:
        if item_entry.item_quantity + quantity >= 0:
            item_entry.item_quantity += quantity
    else:
        if quantity > 0:
            item_entry = basket(item_id = item_id, item_quantity = quantity, session_id = session.id)
            db.session.add(item_entry)
    db.session.commit()
    return jsonify({"success": True, "item_quantity" : item_entry.item_quantity, "item_total_cost" : item_entry.item_total_price})

@app.route('/get_item_description', methods = ['POST'])
def get_item_description():
    data = request.get_json()
    item_id = data.get('item_id')
    item_entry = open_cafe.query.filter_by(id = item_id).first()

    if item_entry:
        return jsonify({"description" : item_entry.description})
    else:
        return jsonify({"error" : "Item not found"}), 404
    
@app.route('/clear_basket', methods = ['POST'])
def clear_basket():
    try: 
        #basket.query.filter_by(user_id=current_user.id).delete()
        session = get_current_session()
        basket.query.filter_by(session_id = session.id).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error clearing basket {e}")
        return jsonify({'success': False, "error": str(e)}), 500
    
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    guest_cookie = session.get('guest_cookie')
    session.clear()
    guest_website = make_response(redirect('/'))

    if guest_cookie:
        guest_website.set_cookie('user_cookie', guest_cookie, max_age = 60*60*24*30)
    else:
        new_cookie = str(uuid.uuid4())
        new_session, new_cookie= create_session()
        db.session.add(new_session)
        db.session.commit()
        guest_website.set_cookie('user_cookie', new_cookie, max_age = 60*60*24*30)
    return guest_website

@app.route('/account', methods = ['GET', 'POST'])
def account_details():
    current_user = get_current_user()
    purchase_history_table = purchase_history.query.filter_by(user_id = current_user.id).all()
    new_password_form = create_new_password_form()
    csrf_token = generate_csrf()

    if current_user:
        if new_password_form.validate_on_submit():
            print('Enter password')
            if current_user.check_password(new_password_form.old_password.data):
                print('password authenticated')
                current_user.password = new_password_form.new_password.data
                db.session.commit()
                flash('Password changed successfully!', 'success')
            else:
                print('Invalid')
                flash('Old password is incorrect.', 'danger')
            return redirect(url_for('account_details'))   
        return render_template('account_info.html', purchase_history_table = purchase_history_table, current_user = current_user, new_password_form = new_password_form, csrf_token = csrf_token)

    
    return redirect('/login')

@app.route('/delete_account', methods = ['POST'])
def delete_account():
    current_user = get_current_user()

    print(current_user)
    print('Inside delete account')
    try:
        sessions = user_session.query.filter_by(user_id=current_user.id).all()
        for each_session in sessions:
            basket.query.filter_by(session_id=each_session.id).delete()
            purchase_history.query.filter_by(session_id=each_session.id).delete()
            db.session.delete(each_session)
        db.session.delete(current_user)
        db.session.commit()

        new_session, new_cookie = create_session()

        response = jsonify({'success': True})
        response.set_cookie('user_cookie', new_cookie, max_age=60 * 60 * 24 * 30)
        return response
        return jsonify({'success' : True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, "error" : str(e)})


if __name__ == '__main__':
    app.run(debug=True)

# Clear up jsonify messages. Set success as False, return the error as e. Also add more try methods, add error handling
# Reduce the redundant html pages? Use if statements to render templates depending on what is passed
# Check the methods (see if they are being used or not)
# Add more secure user handling? Check for any possible security breaches
# Add just coffee into the database?
"""
Allows for calculation of total price in SQL
@total_price.expression
def total_price(cls):
    return cls.item_quantity * open_cafe.price
"""
"""{% extends "base.html" %}
<!DOCTYPE html>
<body>
   <h1> {{ item.name }}</h1>
   <h3>Items Added: </h3>
   <p> {{ basket_entry.item_quantity }} </p>
</body>"""


"""def get_or_create_session(current_cookie):
    session = user_session.query.filter_by(cookie = current_cookie).first()
    if not session:
        session = user_session(cookie = current_cookie)
        db.session.add(session)
        db.session.commit()
    return session"""


#f0edb524-c226-44a9-a6ac-fb8cf306529e



"""def validate(self, extra_validators = None):
        if not super().validate():
            return False
        if not (self.login or self.create):
            self.login.errors.append('Please select an option')
            self.create.errors.append('Please select an option')
            return False"""



"""

<!-- {% block content %}
<h1>Create Account</h1>
<div id = "create_account_form">
   {{ wtf.quick_form(form) }}
</div>
{% endblock %}-->"""

"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
"""