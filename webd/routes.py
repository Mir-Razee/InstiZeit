from webd import application, db, datetime
from flask import redirect, url_for, session, render_template, request, flash
from werkzeug.utils import secure_filename
from webd import oauth, client
import os
from webd.decorator import login_required

def upload(client, img_path):

    config = {
        'album': '2c0C92u',
    }

    print("Uploading image... ")
    image = client.upload_from_path(img_path, anon=False)
    print("Done")
    return image['link']

@application.route("/")
def home(session=session):
    user = dict(session).get('profile', None)
    if user:
        email = user.get("email")
        CHECK_USER = db.execute("SELECT * FROM profile where email=:email", {"email": email}).fetchone()
        mails = db.execute("SELECT email from profile").fetchall()
        pics = db.execute("SELECT imgurl from profile").fetchall()
        for i in range(len(mails)):
            mails[i] = mails[i][0]
            pics[i] = pics[i][0]
        D = dict(zip(mails, pics))
        if CHECK_USER:
            emailto = user.get("email")
            requests = db.execute("SELECT emailfrom FROM friendreq WHERE emailto =:emailto",
                                  {"emailto": emailto}).fetchall()
            for i in range(len(requests)):
                requests[i] = requests[i][0]
            nameinfo = db.execute("SELECT name FROM profile WHERE email = ANY(SELECT emailfrom FROM friendreq WHERE emailto =:emailto);",
                {"emailto": emailto}).fetchall()
            imginfo = db.execute(
                "SELECT imgurl FROM profile WHERE email = ANY(SELECT emailfrom FROM friendreq WHERE emailto =:emailto);",
                {"emailto": emailto}).fetchall()
            for i in range(len(nameinfo)):
                nameinfo[i] = nameinfo[i][0]
            for i in range(len(nameinfo)):
                imginfo[i] = imginfo[i][0]
            ALL_POSTS = db.execute("SELECT * FROM posts").fetchall()
            post_info = []
            all_likes = []
            all_likes2 = []
            for i in ALL_POSTS:
                info = db.execute("SELECT name, imgurl FROM profile where email=:i", {"i": i[1]}).fetchone()
                by_likes = db.execute("SELECT by_email from likes where post_id =:post_id", {"post_id":i[0]}).fetchall()
                dy_likes = [0]*len(by_likes)
                all_likes2.append(by_likes)
                for j in range (len(by_likes)):
                    dy_likes[j] = (D[by_likes[j][0]])
                all_likes.append(dy_likes)
                post_info.append(info)
            print(all_likes)
            print(all_likes2)
            return render_template('home2.html', user=user, ap=ALL_POSTS, pi=post_info,nameinfo=nameinfo,size=len(nameinfo),imginfo=imginfo, al=all_likes, al2=all_likes2)
        else:
            return redirect(url_for('register'))

    return render_template('landing.html')

@application.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@application.route('/authorize')
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

@application.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@application.route('/register', methods=["GET","POST"])
@login_required
def register(session=session):
    user = dict(session).get('profile', None)
    email = user.get("email")
    name = user.get("name")
    pic = user.get("picture")
    if request.method == "POST":

        year=request.form.get("year")
        dept=request.form.get("dept")
        category=request.form.get("category")

        db.execute("INSERT INTO profile(email,name,adm_year,branch,category,imgurl) VALUES(:email, :name, :adm_year,:branch,:category,:imgurl)",
                   {"email": email, "name": name, "adm_year":year, "branch":dept, "category":category,"imgurl":pic})
        db.commit()
        flash('User Registered Successfully!')
        return(redirect(url_for('home')))

    return render_template("register_profile.html",email=email,name=name,pic=pic)

@application.route('/profile')
@login_required
def profile(session=session):
    user = dict(session).get('profile', None)
    pict=user.get("picture")
    email = user.get("email")
    table_data = db.execute("SELECT * FROM profile WHERE email =:email", {"email": email}).fetchone()
    print(table_data)
    if table_data==None:
        return redirect(url_for("register"))

    return render_template('profile.html', pict=pict,table=table_data)

@application.route('/posts', methods=['POST', 'GET'])
@login_required
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
            u1 = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            i1.save(u1)
            url1 = upload(client, u1)
            print(filename, u1, url1)
        if i2.filename != '':
            filename = secure_filename(i2.filename)
            u2 = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            i2.save(u2)
            url2 = upload(client, u2)
            print(filename, u2, url2)

        user = dict(session).get('profile', None)
        email = user.get("email")

        db.execute('''INSERT INTO posts(By_User, Data, Datetime, url1, url2, no_of_likes) 
        VALUES(:By_User, :Data, :Datetime, :url1, :url2, '0')''',
                   {"By_User":email, "Data":text, "Datetime":dt, "url1":url1, "url2":url2})
        db.commit()

        return redirect(url_for('home'))
    return render_template('posts.html')

@application.route('/@/<email>')
@login_required
def getprofile(email):
    user = dict(session).get('profile', None)
    login_email = user.get("email")
    if email == login_email:
        return redirect(url_for("profile"))

    CHECK_USER = db.execute("SELECT * FROM profile where email=:email", {"email":email}).fetchone();
    if CHECK_USER:
        return render_template("getprofile.html", data=CHECK_USER)
    return "No User Found"


@application.route('/msg')
def msg():
    return render_template("msg.html")

@application.route('/addfr')
def addfr(session=session):
    user = dict(session).get('profile',None)
    email = user.get('email')
    result = db.execute("SELECT name FROM profile WHERE NOT email = ANY(SELECT email1 FROM friends) AND NOT email=:email",{"email":email}).fetchall()
    for i in range(len(result)):
        result[i] = result[i][0]
    return render_template('AF.html',result=result,size=len(result))

@application.route('/sendreq', methods=["POST","GET"])
def sendreq(session=session):
    user = dict(session).get('profile',None)
    emailfrom = user.get("email")
    to_name = request.form.get("myName")
    emailto = db.execute("SELECT email FROM profile WHERE name=:name", {"name": to_name}).fetchone()[0]
    db.execute("INSERT INTO friendreq(emailfrom, emailto, state) VALUES(:emailfrom, :emailto, 'Pending')",{"emailfrom":emailfrom,"emailto":emailto})
    db.commit()
    return redirect(url_for('home'))

@application.route('/acceptreq', methods=['POST','GET'])
def accreq(session=session):
    user = dict(session).get('profile', None)
    emailto = user.get("email")
    requests = db.execute("SELECT emailfrom FROM friendreq WHERE emailto =:emailto", {"emailto": emailto}).fetchall()
    for i in range(len(requests)):
        requests[i] = requests[i][0]

    emailfrom = requests[0]
    response = request.form.get('Res')
    print(response,type(response))
    if response=="1":
        db.execute("INSERT INTO friends(email1, email2, status) VALUES(:email1, :email2, '1')",{"email1":emailto, "email2":requests[0]})
        db.execute("INSERT INTO friends(email1, email2, status) VALUES(:email1, :email2, '1')",{"email2":emailto, "email1":requests[0]})
        db.execute("insert into group_chat(group_name) VALUES (CONCAT('friend',:email1,:email2))",{"email1":emailto,"email2":requests[0]})
        group_id=db.execute("select group_id from group_chat where group_name=CONCAT('friend',:email1,:email2)",{"email1":emailto,"email2":requests[0]}).fetchone()
        group_id=group_id[0]
        db.execute("insert into group_users values(:group_id,:email1)",{"group_id":group_id,"email1":emailto})
        db.execute("insert into group_users values(:group_id,:email2)",{"group_id":group_id,"email2":requests[0]})
        db.commit()

    db.execute("DELETE FROM friendreq WHERE emailfrom=:emailfrom",{"emailfrom":emailfrom})
    db.commit()

    return redirect(url_for('home'))

@application.route('/addgrp')
@login_required
def addgrp():
    return render_template('addgrp.html')

@application.route('/creategrp')
def creategrp():
    return render_template('msg.html')


@application.route('/likes/<post_id>', methods=['POST','GET'])
@login_required
def likes(post_id):
    user = dict(session).get('profile', None)
    email = user.get("email")
    check_post = db.execute("SELECT * FROM posts where post_id = :post_id", {"post_id": post_id}).fetchone()
    print(check_post)

    if check_post is None:
        return "Invalid request"

    post_email = check_post[1]
    if email == post_email:
        return redirect(url_for("home"))

    no_of_likes = check_post[6]
    check_like = db.execute("SELECT * FROM likes where post_id=:post_id and by_email=:by_email",
                            {"post_id": post_id, "by_email": email}).fetchone()
    if check_like:
        no_of_likes = no_of_likes - 1
        db.execute("DELETE FROM likes where post_id=:post_id and by_email=:by_email",
                   {"post_id": post_id, "by_email": email})
        db.execute("UPDATE posts SET no_of_likes=:nol WHERE post_id=:post_id", {"nol": no_of_likes, "post_id": post_id})
        db.commit()
    else:
        no_of_likes = no_of_likes + 1
        db.execute("INSERT INTO likes VALUES(:post_id ,:by_email)",
                   {"post_id": post_id, "by_email": email})
        db.execute("UPDATE posts SET no_of_likes=:nol WHERE post_id=:post_id", {"nol": no_of_likes, "post_id": post_id})
        db.commit()
    return redirect(url_for("home"))

@application.route('/show_likes/<post_id>', methods=['POST','GET'])
@login_required
def show_likes(post_id):
    check_post = db.execute("SELECT * FROM posts where post_id = :post_id", {"post_id": post_id}).fetchone()
    print(check_post)

    if check_post is None:
        return "Invalid request"

    get_like_users = db.execute("SELECT by_email from likes where post_id =:post_id", {"post_id":post_id}).fetchall()
    print(get_like_users)

