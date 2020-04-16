from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
import pandas as pd
import datetime

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
df1=pd.read_csv("item.csv")
id=list(df1["IID"])

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home1.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

@app.route("/about_us")
def about_us():
    return render_template('about-us.html')

@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM categories')
            catdata = cur.fetchall()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categoryId, ))
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName, categoryData = catdata)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
    conn.close()
    cluster=int(df1['cluster'].iloc[id.index(int(productId)),])
    gender=df1['gender'].loc[id.index(int(productId)),][0]
    related_products=df1.loc[(df1['cluster']==int(cluster)) & (df1['gender']==gender[0])]

    return render_template("productDescription1.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems,relatedProducts=related_products.to_dict(orient='records'))

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return jsonify({'msg':msg})

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)

@app.route("/checkout")
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT * FROM users WHERE email = ?", (email, ))
        userInfo = cur.fetchone()
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,userInfo=userInfo)

@app.route("/getimages", methods = ['GET'])
def getimages():
    if request.method=='GET':
        prod = request.args.get('product')
        
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT image FROM products WHERE productId=?',(prod,))
            data = cur.fetchone()[0]
            return jsonify({"path":str(data)})
        con.close();

@app.route("/getkart", methods = ['GET'])
def getkart():
    if request.method=='GET':
#        userId = request.args.get('username')
        user = session['email']
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT userId from users WHERE email=?',(user,))
            userId = cur.fetchone()[0];
#            return user 
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
            data = cur.fetchall()
            ret={}
            st="";
            for i in range(len(data)):
                ret[i] = "{\"pid\":\""+str(data[i][0])+"\",\"name\":\""+data[i][1]+"\",\"price\":\""+str(data[i][2])+"\",\"path\":\""+data[i][3]+"\"}"
            if ret:
                return jsonify(ret)
            return jsonify({'msg':'Empty'})
        con.close();

@app.route("/getproducts", methods = ['GET'])
def getproducts():
    if request.method=='GET':

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("SELECT productId, name, price, image FROM products")
            data = cur.fetchall()
            ret={}
            st="";
            for i in range(len(data)):
                ret[i] = "{\"pid\":\""+str(data[i][0])+"\",\"name\":\""+data[i][1]+"\",\"price\":\""+str(data[i][2])+"\",\"path\":\""+data[i][3]+"\"}"
            if ret:
                return jsonify(ret)
            return jsonify({'msg':'Empty'})
        con.close();

@app.route("/getcategory", methods = ['GET'])
def getcategory():
    if request.method=='GET':
        catName = request.args.get('category');
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
#            cur.execute('SELECT categoryId from categories WHERE ')
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, categories WHERE products.categoryId=categories.categoryId AND categories.name=?",(catName,));
            data = cur.fetchall()
            ret={}
            st="";
            for i in range(len(data)):
                ret[i] = "{\"pid\":\""+str(data[i][0])+"\",\"name\":\""+data[i][1]+"\",\"price\":\""+str(data[i][2])+"\",\"path\":\""+data[i][3]+"\"}"
            if ret:
                return jsonify(ret)
            return jsonify({'msg':'Empty'})
        con.close();

@app.route("/removekart", methods = ['GET'])
def removekart():
    if request.method=='GET':
        pid = request.args.get('productId')
        user = session['email']
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT userId from users WHERE email=?',(user,))
            userId = cur.fetchone()[0];
#            return user
            cur.execute("DELETE FROM kart WHERE userId=? AND productId=?", (userId,pid));
            con.commit();
            return jsonify({'msg':'Success'})
        con.close();
        
@app.route('/getrelated', methods=['GET'])
def getrelated():
    if request.method=='GET':
        productId = request.args.get('productId')
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT gender,cluster from products WHERE productId=?',(productId,))
            data = cur.fetchone()
            gender = data[0]
            cluster = data[1]
            cur.execute('select productId,name,price,image from products where cluster=? AND gender=?',(cluster,gender))
            ret=cur.fetchall()
            ret1={}
            for i in range(len(ret)):
                ret1[i]="{\"pid\":\""+str(ret[i][0])+"\",\"name\":\""+ret[i][1]+"\",\"price\":\""+str(ret[i][2])+"\",\"path\":\""+ret[i][3]+"\"}"
        return jsonify(ret1)

@app.route('/confirmCheckout', methods = ['GET'])
def confirmCheckout():
    if request.method=='GET':
        userId=request.args.get('userId');
        
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT productId FROM kart where userId=?',(userId,));
            products = cur.fetchall()
            products1=""
            for prod in products:
                products1 += ','+str(prod[0])
            products=products1[1:]
            ret={}
            cur.execute('SELECT products.price from products, kart WHERE products.productId=kart.productId AND kart.userId=?',(userId,))
            prices=cur.fetchall()
            total=0
            for price in prices:
                total += price[0]
            time=datetime.datetime.now();
            st = 'INSERT INTO transactions ( userId, productId, Amount, time) VALUES ('+str(userId)+', '+products+', '+str(total)+', '+str(time)+')'
            ret[userId]=st
            cur.execute('INSERT INTO transactions ( userId, productId, Amount, time) VALUES (?,?,?,?)',(userId,products,total,time))
            cur.execute('DELETE FROM kart WHERE userId=?',(userId,))
            return jsonify({'Success':ret})
#            return jsonify(ret)
        con.close()
            
@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug=True)
