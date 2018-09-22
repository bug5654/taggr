import sqlite3

#DB in ram
#db = sqlite3.connect(":memory:")
#DB in file
db = sqlite3.connect('mydb')
cursor = db.cursor()
cursor.execute('''
	CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, phone TEXT,
		email TEXT unique, password TEXT)
''')
cursor.execute('''
	INSERT INTO users (id, name, phone, email, password) 
	VALUES (1,"Gypsy","707","gypsy.agee@gmail.com", "meow") 
''')
db.commit()		#notice it's the DB that commits, not the cursor
#when finished
db.close()