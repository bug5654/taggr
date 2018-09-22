import sqlite3

#DB in ram
#db = sqlite3.connect(":memory:")
#DB in file
db = sqlite3.connect('mydb')
cursor = db.cursor()
#cursor.execute('''
#	CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, phone TEXT,#
#		email TEXT unique, password TEXT)
#''')
# users = [
# 	('hiro', '707', 'hiro.agee@gmail.com', 'meow'),
# 	('stranger', '714', 'stranger@gmail.com', 'strangeThingsAreHappeningToMe')
# 	]
# cursor.executemany('''
# 	INSERT INTO users ( name, phone, email, password) 
# 	VALUES (?,?,?,?) 
# ''', users)
# db.commit()		#notice it's the DB that commits, not the cursor

cursor.execute('''SELECT name, email, phone FROM users''')
user1 = cursor.fetchone()
print("first row:", user1)
all_rows = cursor.fetchall()
for row in all_rows:
	print('{0}: {1}, {2}'.format(row[0], row[1], row[2]))
id = cursor.lastrowid
print("last row id: %d" % id)

#when finished
db.close()