from app4 import app, db, open_cafe, recipe, ingredients, ingredient_recipe_amount


cafe_menu = [
    { "name": "Ca Phe Muoi", "price": 5.35, "description": "A salted caramel Vietnamese drink made with a combination of Vietnamese coffee, condensed milk and just a little bit of salt", "image" : "ca phe muoi.jpg"},
    { "name": "Matcha Tonic", "price": 4.20, "description": "A refreshing drink with fruity tones and earthly matcha","image" : "matcha tonic.jpg" },
    { "name": "Irish Coffee", "price": 7.50, "description": "An uplifting caffeinated alcoholic drink made of Irish whiskey, coffee and sweetners.", "image" : "irish coffee.jpg" },
    { "name": "Affogato", "price": 4.75, "description": "A sweet treat made by pouring a shot of espresso over a scoop of vanilla ice cream", "image" : "affogato.jpg" }
]
recipes_data = [
   {
      "name": "Ca Phe Muoi", 
      "ingredients" : [
         {"name" : "Brew Coffee", "amount" : 235},
         {"name" : "Heavy Cream", "amount" : 89},
         {"name" : "Sugar", "amount" : 30},
         {"name" : "Salt", "amount" : 3},
         {"name" : "Milk", "amount" : 120 },
         {"name" : "Cocoa powder", "amount" : 30}
      ]
   },
   {
      "name": "Matcha Tonic", 
      "ingredients" : [
         {"name" : "Strawberry", "amount" : 83},
         {"name" : "Matcha Powder", "amount" : 8},
         {"name" : "Sugar", "amount" : 15},
         {"name" : "Tonic Water", "amount" :235 }
      ]
   },
   {
      "name": "Irish Coffee", 
      "ingredients" : [
         {"name" : "Brew Coffee", "amount" : 470},
         {"name" : "Heavy Cream", "amount" : 320},
         {"name" : "Sugar", "amount" : 17},
         {"name" : "Irish Whiskey", "amount" : 90},
         {"name" : "Chocolate", "amount" : 110}
     ]
   },
   {
      "name": "Affogato", 
      "ingredients" : [
         {"name" : "Espresso", "amount" : 44},
         {"name" : "Vanilla Ice Cream", "amount" : 240},
         {"name" : "Amaretto", "amount" : 20},
         {"name" : "Chocolate", "amount" : 15}
      ]
   }
]

#Carbon Footprint (g CO₂e per g/ml)
# Convert to kg when required?

ingredient_carbon_footprint = [
   {"name" : "Brew Coffee", "carbon_footprint" : 0.25},
   {"name" : "Heavy Cream", "carbon_footprint" : 3.77},
   {"name" : "Sugar", "carbon_footprint" : 0.24},
   {"name" : "Salt", "carbon_footprint" : 0.20},
   {"name" : "Milk", "carbon_footprint" : 1},
   {"name" : "Cocoa powder", "carbon_footprint" : 1.40},
   {"name" : "Strawberry", "carbon_footprint" : 0.22},
   {"name" : "Matcha Powder", "carbon_footprint" : 1.90},
   {"name" : "Tonic Water", "carbon_footprint" : 0.30},
   {"name" : "Irish Whiskey", "carbon_footprint" : 2},
   {"name" : "Chocolate", "carbon_footprint" : 5},
   {"name" : "Espresso", "carbon_footprint" : 0.28},
   {"name" : "Vanilla Ice Cream", "carbon_footprint" : 1.50},
   {"name" : "Amaretto", "carbon_footprint" : 2}
]



with app.app_context():
   db.create_all()

   for item in cafe_menu:
      item_entry = open_cafe.query.filter_by(name=item["name"]).first()
      if not item_entry:
         item_entry = open_cafe(name = item["name"], price = item["price"], description = item["description"], image = item["image"])
         db.session.add(item_entry) 
   db.session.commit()

   for ingredient in ingredient_carbon_footprint:
      ingredient_entry = ingredients.query.filter_by(name = ingredient['name']).first()
      if not ingredient_entry:
         ingredient_entry = ingredients(name = ingredient["name"], carbon_footprint = ingredient["carbon_footprint"])
         db.session.add(ingredient_entry)
   db.session.commit()

   for recipe_data in recipes_data:
      item = open_cafe.query.filter_by(name = recipe_data["name"]).first()
      if not item:
         print(f"No item found for recipe {recipe_data['name']}")
         continue

      recipe_entry = recipe(item_id = item.id)
      db.session.add(recipe_entry)
      db.session.flush()

      for ingredient in recipe_data["ingredients"]:
         ingredient_entry = ingredients.query.filter_by(name = ingredient["name"]).first()
         if not ingredient_entry:
            print(f"Ingredient not found {ingredient['name']}")
            continue

         connection = ingredient_recipe_amount(recipe_id = recipe_entry.id, ingredient_id = ingredient_entry.id, amount = ingredient["amount"])
         db.session.add(connection)
   db.session.commit()


