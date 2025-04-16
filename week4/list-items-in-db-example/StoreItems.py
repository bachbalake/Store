'''Script to populate the database with some initial data.
   In reality you would probably create a separate editor or a tool for importing data from elsewhere,
   but for CM1102 we'll just use this script to populate the database.'''

from ListItems import app, db, Technology

technologies = [
    { "name": "HTML", "taught": "Autumn semester", "description": "HTML is the standard markup language for creating Web pages." },
    { "name": "CSS", "taught": "Autumn semester", "description": "CSS is a language that describes the style of an HTML document." },
    { "name": "JavaScript", "taught": "Spring semester", "description": "JavaScript is the programming language of HTML and the Web because it runs in all modern browsers." },
    { "name": "Python/Flask", "taught": "Spring semester", "description": "Flask is a popular server side framework for writing web applications in Python." },
    { "name": "SQL", "taught": "Spring semester", "description": "SQL is a standard language for storing, manipulating and retrieving data in databases." },
    { "name": "Perl", "taught": "Aaaaaah please no!", "description": "What is this, 1999?" }
]

# Bear in mind this script does NOT run the app
# instead we use app.app_context() which Flask provides to allow us to use the app's configuration and extensions
with app.app_context():
    db.create_all() # creates the empty tables
    
    for tech in technologies:
        newTech = Technology(name=tech["name"], taught=tech["taught"], description=tech["description"])
        db.session.add(newTech)
    
    db.session.commit()


