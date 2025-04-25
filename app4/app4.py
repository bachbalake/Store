from flask import Flask, render_template, request, jsonify, make_response, redirect
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, EmailField, PasswordField
from wtforms.validators import NumberRange, DataRequired, Regexp, ValidationError, Email, Length, EqualTo
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.hybrid import hybrid_property
from flask_wtf.csrf import CSRFProtect, generate_csrf
import uuid
from datetime import datetime

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

class user_session(db.Model):
    __tablename__ = 'user_cookies_session'
    id = db.Column (db.Integer, primary_key = True)
    cookie = db.Column (db.String(100), unique = True, nullable = False)
    creation_time = db.Column (db.DateTime, default = datetime.utcnow)

    session_basket = db.relationship('basket', backref = 'session', lazy = True)

    @hybrid_property
    def total_basket_price(self):
        return round(sum(item.item_total_price for item in self.session_basket), 2)


"""
class user(db.Model):
    __tablename__ = 'User Information'
    id = db.Column (db.Integer, primary_key = True)
    name = db.Column (db.String(45), index = True, unique = True, nullable = False)
    password = db.Column (db.String(24), unique = True, nullable = False) # Make it so the password is hidden?
    basket_id = db.Column (db.Integer) # It is a foreign key, the parent key is a basket record. I want to create a new basket when a new user is created
class user_list (db.Model):
    __tablename__ = 'Users List'
    user_id = db.Column (db.Integer) # This is a foreign key, its parent is id from user
    purchase_amount = db.Column (db.Float) # Using the basket it calculates through the amount bought and price the total money spent by the user
"""

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



    

def create_session(new_cookie):
    session = user_session(cookie = new_cookie)
    db.session.add(session)
    db.session.commit()
    return session

def get_current_session():
    user_cookie = request.cookies.get('user_cookie')
    session = user_session.query.filter_by (cookie = user_cookie).first()
    return session


@app.route('/')
def galleryPage():
    cafe_menu = open_cafe.query.all()
    cafe_recipes = recipe.query.all()
    csrf_token = generate_csrf()
    user_cookie = request.cookies.get('user_cookie')
    if not user_cookie:
        new_cookie = str(uuid.uuid4())
        cookie_website = make_response(render_template('index.html',cafe_menu = cafe_menu, cafe_recipes = cafe_recipes, csrf_token = csrf_token))
        cookie_website.set_cookie('user_cookie', new_cookie, max_age = 60 * 60 * 24 * 30)
        current_session = create_session(new_cookie)
        return cookie_website
    current_session = get_current_session()
    return render_template('index.html',cafe_menu = cafe_menu, cafe_recipes = cafe_recipes, csrf_token = csrf_token)


@app.route('/product_page/<int:item>', methods = ['GET', 'POST'])
def singleProductPage(item):
    purchase_form = Basket_form()
    selected_item = open_cafe.query.get_or_404(item)
    current_session = get_current_session()
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

        return render_template('PurchaseProduct.html', item=selected_item, quantity_added = quantity, basket_entry=item_entry) 
    else: 
        return render_template('SingleProduct.html', cafe_item = selected_item, basket = purchase_form)
    
# @app.route('user/basket')
@app.route('/basket')
def basketPage():
    session = get_current_session()
    user_basket = basket.query.filter_by(session_id = session.id).all()
    csrf_token = generate_csrf()
    return render_template('ViewBasket.html', user_basket = user_basket, csrf_token = csrf_token)

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

@app.route('/checkout/start', methods = ['GET', 'POST'])
def checkout_start():
    checkout_choice_form = checkout_form()
    if checkout_choice_form.validate_on_submit():
        if checkout_choice_form.login.data:
            return redirect ('/login')
        else:
            session = get_current_session()
            user_basket = basket.query.filter_by(session_id = session.id).all()
            payment_form = credit_card_form()

            if payment_form.validate_on_submit():
                return redirect('/checkout/complete')
    
            return render_template('checkout.html', user_basket = user_basket, payment_form = payment_form, session = session)

    return render_template('start_checkout.html', choice_form = checkout_choice_form)

@app.route('/checkout/guest', methods = ['GET', 'POST'])
def checkout_guest():
    session = get_current_session()
    user_basket = basket.query.filter_by(session_id = session.id).all()
    payment_form = credit_card_form()

    if payment_form.validate_on_submit():
       return redirect('/checkout/complete')
    
    return render_template('checkout.html', user_basket = user_basket, payment_form = payment_form, session = session)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_choice = login_or_create_form()

    if login_choice.validate_on_submit():
        if login_choice.login.data:
            return render_template('login.html')
        elif login_choice.create.data:
            return redirect ('/create_account')

    return render_template('login.html', login_or_create_form = login_choice)

@app.route('/create_account', methods = ['POST', 'GET'])
def create_account():
    create_form = create_account_form()

    if create_form.validate_on_submit():
        return redirect ('/login')
    
    return render_template ('create_account.html', form = create_form)

@app.route('/checkout/complete')
def checkout_complete():
    return render_template('checkout_complete.html')
if __name__ == '__main__':
    app.run(debug=True)

# Clear up jsonify messages. Set success as False, return the error as e. Also add more try methods, add error handling
# Reduce the redundant html pages? Use if statements to render templates depending on what is passed
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