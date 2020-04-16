import sqlite3
import pandas as pd

#Open database
db = pd.read_csv('item.csv')
#
#with sqlite3.connect('database.db') as conn:
#	curr = conn.cursor()
#	li=['jeans','kids','shirts','tshirts']
#	for i in li:
#		curr.execute('INSERT INTO categories (name) VALUES (?)',(i,))
#conn.close()


with sqlite3.connect('database.db') as conn:
    curr = conn.cursor()
    curr.execute('DROP TABLE products')
    conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
        gender TEXT,
        color TEXT,
		categoryId INTEGER,
        cluster INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')
    for row in range(145):
        print(db['IID'][row])
#        st = 'INSERT INTO products (name, price, description, image, stock, gender, color, categoryId, cluster) VALUES('+str(db['name'][row])+','+str(db['price'][row])+','+str(db['brand'][row])+','+str(db['path'][row])+','+str(db['stock'][row])+','+str(db['gender'][row])+','+str(db['color'][row])+','+str(db['category'][row])+','+str(int(db['cluster'][row]))+')'
#        print(st)
        curr.execute('INSERT INTO products (name, price, description, image, stock, gender, color, categoryId, cluster) VALUES(?,?,?,?,?,?,?,?,?)',(str(db['name'][row]),str(db['price'][row]),str(db['brand'][row]),str(db['path'][row]),str(db['stock'][row]),str(db['gender'][row]),str(db['color'][row]),str(db['category'][row]),str(db['cluster'][row])))
        print(db['IID'][row])
        print(curr)
conn.close()


#with sqlite3.connect('database.db') as conn:
#    conn.execute('DROP TABLE transactions')
#    conn.execute('''CREATE TABLE transactions
#        (tranID INTEGER PRIMARY KEY,
#        userId INTEGER,
#        productId TEXT,
#        Amount REAL,
#        time timestamp,
#        FOREIGN KEY(userId) REFERENCES users(userId),
#        FOREIGN KEY(productId) REFERENCES products(productId)
#        )''')
#conn.close()
