from webd import app, db, datetime
from flask import redirect, url_for, session, render_template, request, flash
from werkzeug.utils import secure_filename
from webd import oauth, client
import os

def upload(client, img_path):

    config = {
        'album': '2c0C92u',
    }

    print("Uploading image... ")
    image = client.upload_from_path(img_path, anon=False)
    print("Done")
    return image['link']

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/home")
def home(session=session):
    user = dict(session).get('profile', None)
    if user:
        email = user.get("email")
        CHECK_USER = db.execute("SELECT * FROM profile where email=:email", {"email": email}).fetchone()
        if CHECK_USER:
            ALL_POSTS = db.execute("SELECT * FROM Posts").fetchall()
            post_info = []
            for i in ALL_POSTS:
                info = db.execute("SELECT name, imgurl FROM profile where email=:i", {"i": i[1]}).fetchone()
                post_info.append(info)
            return render_template('home2.html', user=user, ap=ALL_POSTS, pi=post_info)
        else:
            return redirect(url_for('register'))

    return render_template('landing.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after browser gets closed
    return redirect(url_for('home')) ##

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/register', methods=["GET","POST"])
def register(session=session):
    user = dict(session).get('profile', None)
    email = user.get("email")
    name = user.get("name")
    pic = user.get("picture")
    if request.method == "POST":

        year=request.form.get("year")
        dept=request.form.get("dept")
        category=request.form.get("category")

        db.execute("INSERT INTO Profile(email,name,adm_year,branch,category,imgurl) VALUES(:email, :name, :adm_year,:branch,:category,:imgurl)",
                   {"email": email, "name": name, "adm_year":year, "branch":dept, "category":category,"imgurl":pic})
        db.commit()
        flash('User Registered Successfully!')
        return(redirect(url_for('home')))

    return render_template("register_profile.html",email=email,name=name,pic=pic)

@app.route('/profile')
def profile(session=session):
    user = dict(session).get('profile', None)
    pict=user.get("picture")
    email = user.get("email")
    table_data = db.execute("SELECT * FROM Profile WHERE email =:email", {"email": email}).fetchone()
    print(table_data)
    if table_data==None:
        return redirect(url_for("register"))

    return render_template('profile.html', pict=pict,table=table_data)

@app.route('/posts', methods=['POST', 'GET'])
def posts(session=session):
    if request.method == "POST":
        now = datetime.now()
        dt = now.strftime("%H:%M, %B %d")
        text = request.form.get('text')
        i1 = request.files['u1']
        i2 = request.files['u2']
        print(i1, i2, type(i1), type(i2))
        url1 = None; url2 = None;
        if i1.filename != '':
            filename = secure_filename(i1.filename)
            u1 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            i1.save(u1)
            url1 = upload(client, u1)
            print(filename, u1, url1)
        if i2.filename != '':
            filename = secure_filename(i2.filename)
            u2 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            i2.save(u2)
            url2 = upload(client, u2)
            print(filename, u2, url2)

        user = dict(session).get('profile', None)
        email = user.get("email")

        db.execute("INSERT INTO Posts(By_User, Data, Datetime, url1, url2) VALUES(:By_User, :Data, :Datetime, :url1, :url2)",
                   {"By_User":email, "Data":text, "Datetime":dt, "url1":url1, "url2":url2})
        db.commit()

        return redirect(url_for('home'))
    return render_template('posts.html')

@app.route('/@/<email>')
def getprofile(email):
    print(email, type(email))
    CHECK_USER = db.execute("SELECT * FROM Profile where email=:email", {"email":email}).fetchone();
    if CHECK_USER:
        return render_template("getprofile.html", data=CHECK_USER)
    return "No User Found"