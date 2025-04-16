from app4 import app, db, open_cafe


cafe_menu = [
    { "name": "Ca Phe Muoi", "price": 5.35, "description": "A salted caramel Vietnamese drink made with a combination of Vietnamese coffee, condensed milk and just a little bit of salt", "image" : "ca phe muoi.jpg"},
    { "name": "Matcha Tonic", "price": 4.20, "description": "A refreshing drink with fruity tones and earthly matcha","image" : "matcha tonic.jpg" },
    { "name": "Irish Coffee", "price": 7.50, "description": "An uplifting caffeinated alcoholic drink made of Irish whiskey, coffee and sweetners.", "image" : "irish coffee.jpg" },
    { "name": "Affogato", "price": 4.75, "description": "A sweet treat made by pouring a shot of espresso over a scoop of vanilla ice cream", "image" : "affogato.jpg" }
]


with app.app_context():
   db.create_all()
   for item in cafe_menu:
      item_entry = open_cafe(name = item["name"], price = item["price"], description = item["description"], image = item["image"])
      db.session.add(item_entry)
   db.session.commit()