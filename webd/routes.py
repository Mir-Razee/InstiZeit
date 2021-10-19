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
    user = dict(session).get('profile', None)
    if user:
        email = user.get("email")
        CHECK_USER = db.execute("SELECT * FROM profile where email=:email", {"email": email}).fetchone()
        print(CHECK_USER)
        if CHECK_USER:
            ALL_POSTS = db.execute("SELECT * FROM Posts").fetchall()
            post_info=[]
            for i in ALL_POSTS:
                info = db.execute("SELECT name, imgurl FROM profile where email=:i", {"i":i[1]}).fetchone()
                post_info.append(info)
            print(ALL_POSTS)
            print(post_info)
            return render_template('home2.html', user=user, ap=ALL_POSTS, pi=post_info)
        else:
            return render_template('register.html', user=user)

    return render_template('landing.html')

@app.route("/home")
def home(session=session):

    # user = dict(session).get('profile', None)
    # if user:
    #     email = user.get("email")
    #     CHECK_USER = db.execute("SELECT * FROM profile where email=:email", {"email": email}).fetchone()
    #     print(CHECK_USER)
    #     if CHECK_USER:
    #         # url = user.get("hasImage")
    #         #print(url)
    #         ALL_POSTS = db.execute("SELECT * FROM Posts").fetchall()
    #         names=[]
    #         for i in ALL_POSTS:
    #             name = db.execute("SELECT name FROM profile where email=:i", {"i":i[1]}).fetchone()
    #             names.append(name[0])
    #         print(ALL_POSTS)
    #         print(names)
    #         return render_template('home2.html',user=user, ap = ALL_POSTS, names=names)
    #     else:
    #         return render_template('register.html', user=user)

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
    print(user_info)
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after browser gets closed
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/posts', methods=['POST', 'GET'])
def posts(session=session):
    if request.method == "POST":
        flash("Uploading Images please wait", "success")
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

        return render_template('home2.html')
    return render_template('posts.html')
