"""
admin user has access to special features
username: admin
password: admin
"""

from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from database import get_db,close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, SearchLocationForm, SearchActivityForm, LoginForm, CommentForm, BookingForm, UpdateForm, AddDestinationForm, ActivityForm
from functools import wraps
from datetime import date, timedelta

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_request(e=None):
    close_db(e)

@app.before_request
def load_logged_in_user():
    """
        if logged in, users icon displayed
    """
    g.user = session.get("username",None)
    if g.user != None:
        db = get_db()
        g.icon = db.execute("SELECT icon FROM login WHERE username = ?",(g.user,)).fetchone()["icon"]

def login_required(view):
    """
    if login needed, auto login if possible
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user == None:
            return redirect(url_for("auto_login_check",next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin(view):
    """
    if username = admin, extra features available
    password: admin
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user != "admin":
            return redirect(url_for("home"))
        return view(**kwargs)
    return wrapped_view

@app.route("/", methods=["GET","POST"])
def index():
    """
    start route must be "/", directs straight to home page 
    """
    return redirect("home")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    details entered to user database if no user with that username

    cookie given which can be used to auto login, lasts 7 days

    redirects to auto login function so it happens when you submit
    """
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        surname = form.surname.data
        icon = form.icon.data
        db = get_db()
        if db.execute("SELECT username FROM login WHERE username = ?",(username,)).fetchone() is not None:
            form.username.errors.append("Username already taken")
            db.execute("INSERT INTO errors (username,error) VALUES (NULL,'Username already taken');")
            # Table that holds errors made by users for admin to see
            db.commit()
        else:
            db.execute("INSERT INTO login (username, password, first_name, surname, icon ) VALUES (?,?,?,?,?)",(username, generate_password_hash(password),first_name,surname,icon))
            db.commit()

            response = make_response(redirect("auto_login_check"))
            response.set_cookie("username",username,max_age=(60*60*24*7))
            return response
    return render_template("register.html",form=form)


@app.route("/login", methods=["GET","POST"])
def login():
    """
    if username/password is wrong returns help message
    
    clears session and sets session["username"] as username, becomes g.user

    cookie given which can be used to auto login, lasts 7 days
    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()
        user = db.execute("SELECT password FROM login WHERE username = ?",(username,)).fetchone()
        if user is None:
            form.username.errors.append("Not a valid user")
            db.execute("INSERT INTO errors (username,error) VALUES (NULL,'Not a valid user');")
            db.commit()
        elif not check_password_hash(user["password"],password ):
            form.password.errors.append("Incorrect password")
            db.execute("INSERT INTO errors (username,error) VALUES (?,'Incorrect password');",(g.user,))
            db.commit()
        else:
            session.clear()
            session["username"] = username
            next_page = request.args.get("next")
            if not next_page:
                response = make_response( redirect( url_for('home')) )
            else:
                response = make_response( redirect(next_page) )
            response.set_cookie("username",username,max_age=(60*60*24*7))
            return response
    return render_template("login.html",form=form)


@app.route("/auto_login_check", methods=["GET","POST"])
def auto_login_check():
    """
    Checks for username cookie

    if found logs in as that user

    else redirects to login (not registered or cookie expired or was deleted)
    """
    if request.cookies.get("username"):
        session.clear()
        session["username"] = request.cookies.get("username")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("home")
        else:
            return redirect( next_page )
    return redirect( "login" )


@app.route("/home", methods=["GET","POST"])
def home():
    """
        greets by user's name

        if not logged in shows welcome page
        else link to "forget details"
        shows links previously visited pages with new discounts
    """
    db = get_db()
    if g.user:
        user = db.execute(""" SELECT first_name, surname FROM login WHERE username = ? """,(g.user,)).fetchone()
        searches = []
        for i in range(db.execute("SELECT COUNT(place) AS count FROM destinations").fetchone()["count"]):
            if request.cookies.get(str(i+1)) == str(i+1):
                # runs through auto incremented ID's for all places in database
                # if cookie present, will be displayed (location page has been visited)
                searches.append(db.execute("SELECT * FROM destinations WHERE location_id = ?",(i+1,)).fetchone())
        
        userCookie = False
        if request.cookies.get("username"):
            userCookie = True
            
        return render_template("home.html",user=user, searches=searches, userCookie=userCookie)
    return render_template("home.html")


@app.route("/search_by_location", methods=["GET","POST"])
@login_required
def search_by_location():
    """
    searches for place names
    takes input: "Cobh" returns Cobh, "C" returns Cobh, Cappanalea...
    radio input decides order
    """
    form = SearchLocationForm()
    view = False
    if form.validate_on_submit():
        search = form.search.data
        order = form.order.data
        if order == "Alphabetical":
            order = "place"
        elif order == "Highest Rating":
            order = "rating DESC"
        search = "'"+search+"%'"
        db = get_db()
        view = db.execute("SELECT * FROM destinations WHERE place LIKE "+ search +" ORDER BY "+order).fetchall()
    return render_template("search.html",form=form,view=view)

@app.route("/search_by_activity", methods=["GET","POST"])
@login_required
def search_by_activity():
    """
    uses all activities from database as select choices
    """
    form = SearchActivityForm()
    view = False
    activityList = []
    db = get_db()
    choices = db.execute("""SELECT DISTINCT activity FROM activities ORDER BY activity;""").fetchall()
    for choice in choices:
        activityList.append(choice["activity"])
    form.search.choices = activityList

    if form.validate_on_submit():
        search = form.search.data
        order = form.order.data
        if order == "Alphabetical":
            order = " ORDER BY d.place"
        else: 
            order = " ORDER BY d.rating DESC"
        db = get_db()
        view = db.execute("SELECT * FROM destinations AS d JOIN activities AS a ON d.location_id = a.location_id WHERE a.activity = ? "+order,(search,)).fetchall()
    return render_template("search.html",form=form,view=view)


@app.route("/location/<location_id>", methods=["GET","POST"])
@login_required
def location(location_id):
    """
    img url found by manipulating the name

    cookie added for targeted advertising in homepage

    comment form updates average rating in database
    """
    form=CommentForm()
    db = get_db()
    if form.validate_on_submit():
        comment = form.comment.data
        rating = form.rating.data
        username = db.execute("SELECT username FROM login WHERE username = ?",(g.user,)).fetchone()["username"]
        db.execute("INSERT INTO comments (username, location_id, comment, rating) VALUES (?,?,?,?);",(username, location_id,comment, rating))
        
        average = round( db.execute("SELECT AVG(rating) AS average FROM comments WHERE location_id = ?",(location_id,)).fetchone()["average"], 2 )
        db.execute("""UPDATE destinations SET rating = ? WHERE location_id = ?""",(average,location_id))
        db.commit()
    
    details = db.execute("SELECT * FROM destinations WHERE location_id = ?",(location_id,)).fetchone()
    activities = db.execute("SELECT * FROM activities WHERE location_id = ?",(location_id,)).fetchall()
    comments = db.execute("SELECT * FROM comments WHERE location_id = ?",(location_id,)).fetchall()
    
    img = details["place"]
    img = img.lower()
    img = img.replace(" ","")
    img = img.replace(".","")
    img += ".jpg"
    
    response = make_response(render_template("location.html",form=form, details=details, activities=activities,comments=comments, location_id=location_id, img=img))
    response.set_cookie(location_id,location_id,max_age=(60*60*24*7))
    return response

@app.route("/bookings", methods=["GET","POST"])
@login_required
def bookings():
    db = get_db()
    user_bookings = db.execute("SELECT * FROM bookings AS b JOIN destinations AS d ON b.location_id = d.location_id WHERE b.username = ?",(g.user,)).fetchall()
    return render_template("booking.html",bookings=user_bookings)

@app.route("/booking/<int:location_id>/<int:discount>", methods=["GET","POST"])
@login_required
def booking(location_id,discount):
    """
    Choose dates for holiday

    total nights gotten from dates

    added to bookings database
    """
    form = BookingForm()
    if discount < 0 or discount > 15: #if user tries to cheat (get huge discount by changing url, discount is 0
        discount = 0
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        db = get_db()
        pricePerNight = db.execute("SELECT price FROM destinations WHERE location_id = ?",(location_id,)).fetchone()["price"]
        
        # Functions used for date manipulation
        #https://www.w3resource.com/python-exercises/python-basic-exercise-14.php
        #https://www.programiz.com/python-programming/datetime/strftime


        s_date = date(int(start_date.strftime("%Y")), int(start_date.strftime("%m")), int(start_date.strftime("%d")))
        e_date = date(int(end_date.strftime("%Y")), int(end_date.strftime("%m")), int(end_date.strftime("%d")))
        nights = e_date - s_date
        nights = nights.days # difference between dates in days

        if nights < 0:
            form.end_date.errors.append("End Date must be after Start Date")
            db.execute("INSERT INTO errors (username,error) VALUES (?,'End Date must be after Start Date');",(g.user,))
            db.commit()
        else:
            db.execute("INSERT INTO bookings (location_id,username,start_date,end_date,nights,price,paid) VALUES (?,?,?,?,?,?,?)",(location_id,g.user,start_date,end_date,nights,round(pricePerNight*nights-(pricePerNight*nights*(discount/100)),2),"0"))
            db.commit()
            return redirect(url_for("bookings"))
    return render_template("bookingForm.html",form=form)

@app.route("/cancel_booking/<booking_id>",methods=["GET","POST"])
@login_required
def cancel_booking(booking_id):
    db = get_db()
    username = db.execute("SELECT username FROM bookings WHERE booking_id = ?",(booking_id,)).fetchone()
    if g.user == username["username"]:
        db.execute("DELETE FROM bookings WHERE booking_id = ?",(booking_id,))
        db.commit()
        return redirect(url_for('bookings'))

@app.route("/timetable/<booking_id>", methods=["GET","POST"])
@login_required
def timetable(booking_id):
    """
    Generated using loops/functions in HTML

    Displays timetable for days in specific holiday 

    form adds activity into timetable
    """
    form = ActivityForm()
    activityList = []
    db = get_db()
    details = db.execute("""    SELECT DISTINCT a.activity, d.place, b.start_date, b.end_date, b.nights
                                FROM activities AS a
                                JOIN bookings AS b
                                JOIN destinations AS d
                                ON a.location_id = d.location_id
                                AND a.location_id = b.location_id
                                WHERE b.booking_id = ?
                                ORDER BY a.activity;""",(booking_id,)).fetchall()
    for activity in details:
        activityList.append(activity["activity"])
    form.activity.choices = activityList
    if form.validate_on_submit():
        time = form.time.data
        activity = form.activity.data
        date = form.date.data
        bookingDates = db.execute("""SELECT * FROM bookings WHERE booking_id = ?""",(booking_id,)).fetchone()
        if bookingDates["start_date"] > date or bookingDates["end_date"] - timedelta(days=1) < date:
            form.time.errors.append("Please try a date during your holiday")
            db.execute("INSERT INTO errors (username,error) VALUES (?,'Please try a date during your holiday');",(g.user,))
        else:
            if db.execute("""SELECT * FROM activityBookings WHERE booking_id = ? AND time = ? AND date = ?""",(booking_id,time,date)).fetchone() is None:
                db.execute("INSERT INTO activityBookings VALUES (?,?,?,?)",(booking_id,activity,date,time))
            else:
                form.time.errors.append("You already have an activity at this time")
                db.execute("INSERT INTO errors (username,error) VALUES (?,'You already have an activity at this time');",(g.user,))
    db.commit()
    timetable = db.execute("SELECT * FROM activityBookings WHERE booking_id = ?",(booking_id,)).fetchall()
    # render template passes in functions to be used in the jinja
    return render_template("timetable.html", form=form, details=details, timetable=timetable, timedelta=timedelta, str=str)



@app.route("/delete_cookie/<cookie>",methods=["GET","POST"])
def delete_cookie(cookie):
    """
    sets expire time to the past, deletes straight away
    """
    response = redirect(url_for('home'))
    response.set_cookie(cookie, '', expires=0)
    return response

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(error):
    """
    if error 404 occurs

    gives back error page
    """
    return render_template("error.html"),404



# ADMIN ONLY SECTION

@app.route("/dbCheck/<table>", methods=["GET","POST"])
@admin #Only admin user can access 
def dbCheckTable(table):
    """
    table cannot be inputted into sql query, 
    string made outside, passed in
    """
    if table != "menu":
        db = get_db()
        select = "SELECT * FROM "+table
        view = db.execute(select).fetchall()
    else:
        view = False
    return render_template("dbCheck.html",view=view)


@app.route("/delete_data/<table>/<check1>/<check2>", methods=["GET","POST"])
@admin
def delete_data(table,check1,check2):
    """
    2 checks to make sure correct row is deleted

    query assembled based on table and columns used in that table
    """
    db = get_db()
    query = "DELETE FROM "+table+" WHERE "
    if table == "destinations":
        query += "location_id = '"+check1+"' AND place = '"+check2+"'"
    elif table == "comments":
        query += "comment = '"+check1+"' AND username = '"+check2+"'"
    elif table == "login":
        query += "user_id = '"+check1+"' AND username = '"+check2+"'"
    elif table == "activities":
        query += "location_id = '"+check1+"' AND activity = '"+check2+"'"
    elif table == "bookings":
        query += "booking_id = '"+check1+"' AND username = '"+check2+"'"
    db.execute(query)
    db.commit()
    return redirect(url_for("dbCheckTable",table=table))

@app.route("/auto_update_paid",methods=["GET","POST"])
@admin
def auto_update_paid():
    """
    pay on arrival system

    if start date of holiday is passed, assume payment was made
    """
    db = get_db()
    bookings = db.execute("SELECT * FROM bookings").fetchall()
    print(bookings)
    for booking in bookings:
        if booking["start_date"] <= date.today():
            db.execute("UPDATE bookings SET paid = '1' WHERE booking_id = ?;",(booking["booking_id"],))
            db.commit()
    return redirect(url_for("dbCheckTable",table='menu'))


@app.route("/manual_updateView", methods=["GET","POST"])
@admin
def manual_updateView():
    form = UpdateForm()
    tableData = []
    tables = ["destinations","login","bookings"]
    db = get_db()
    for table in tables:
        query = "SELECT * FROM "+table
        tableData.append(db.execute(query).fetchall())
    return render_template("manual_update.html", form=form, tableData=tableData)


@app.route("/manual_updateDestinations", methods=["GET","POST"])
@admin
def manual_updateDestinations():
    """
    can change one entry in database given row ID
    """
    form = UpdateForm()
    tableData = []
    db = get_db()
    if form.validate_on_submit:
        query = "UPDATE destinations SET "
        if form.update2.data:
            query += "place = "+"'"+form.update2.data
        elif form.update3.data:
            query += "county = "+"'"+form.update3.data
        elif form.update4.data:
            query += "description = "+"'"+form.update4.data
        elif form.update5.data:
            query += "rating = "+"'"+form.update5.data
        query += "' WHERE location_id = " + str(form.updateID.data)+";"
        db.execute(query)
        db.commit()
    return redirect(url_for("manual_updateView"))

@app.route("/manual_updateLogin", methods=["GET","POST"])
@admin
def manual_updateLogin():
    form = UpdateForm()
    tableData = []
    db = get_db()
    if form.validate_on_submit:
        query = "UPDATE login SET "
        if form.update2.data:
            query += "username = "+"'"+form.update2.data
        elif form.update3.data:
            query += "first_name = "+"'"+form.update3.data
        elif form.update4.data:
            query += "surname = "+"'"+form.update4.data
        elif form.update5.data:
            query += "icon = "+"'"+form.update5.data
        query += "' WHERE user_id = " + str(form.updateID.data)+";"
        db.execute(query)
        db.commit()
    return redirect(url_for("manual_updateView"))

@app.route("/manual_updateBookings", methods=["GET","POST"])
@admin
def manual_updateBookings():
    form = UpdateForm()
    db = get_db()
    if form.validate_on_submit:
        query = "UPDATE bookings SET "
        if form.update2.data:
            query += "location_id = "+"'"+form.update2.data
        elif form.update3.data:
            query += "start_date = "+"'"+form.update3.data
        elif form.update4.data:
            query += "end_date = "+"'"+form.update4.data
        elif form.update5.data:
            query += "price = "+"'"+form.update5.data
        query += "' WHERE booking_id = " + str(form.updateID.data)+";"
        db.execute(query)
        db.commit()
    return redirect(url_for("manual_updateView"))


@app.route("/add_destination",methods=["GET","POST"])
@admin
def add_destination():
    """
    adds destination to database
    """
    form = AddDestinationForm()
    if form.validate_on_submit():
        place = form.place.data
        county = form.county.data
        description = form.description.data
        rating = form.rating.data
        price = form.price.data
        db = get_db()
        db.execute("""  INSERT INTO destinations 
                        (place,county,description,rating,price)
                        VALUES 
                        (?,?,?,?,?);""",(place,county,description,rating,price))
        db.commit()
        return redirect(url_for('dbCheckTable',table = "destinations"))
    return render_template("add_destination.html",form=form)

@app.route("/toolbar/<view>", methods=["GET","POST"])
@admin
def toolbar(view):
    """
    links to all admin tool

    number of errors made by users with icon(clickable)
    on click shows all errors and user who made them

    "clear errors" deletes stored errors
    """
    db = get_db()
    if view == "delete_view":
        db.execute("DELETE FROM errors")
        db.commit()
    count = db.execute("SELECT COUNT(*) AS count FROM errors").fetchone()["count"]
    errors = db.execute(""" SELECT * FROM errors""").fetchall()
    return render_template("toolbar.html", errors=errors, count=count, view=view)