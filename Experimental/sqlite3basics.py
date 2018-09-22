import sqlite3

#DB in ram
#db = sqlite3.connect(":memory:")
#DB in file
db = sqlite3.connect('mydb')
cursor = db.cursor()
#cursor.execute('''
#	CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, phone TEXT,
#		email TEXT unique, password TEXT)
#''')
users = [
	('hiro', '707', 'hiro.agee@gmail.com', 'meow'),
	('stranger', '714', 'stranger@gmail.com', 'strangeThingsAreHappeningToMe')
	]
cursor.executemany('''
	INSERT INTO users ( name, phone, email, password) 
	VALUES (?,?,?,?) 
''', users)
db.commit()		#notice it's the DB that commits, not the cursor
#when finished
db.close()