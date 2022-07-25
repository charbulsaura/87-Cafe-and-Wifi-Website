# WEBSITE: Cafe & Wifi
"""
On day 66/62, we create an API that serves data on cafes with wifi and good coffee.
Today, you're going to use the data from that project to build a fully-fledged website to display the information.

Included in this assignment is an SQLite database called cafes.db that lists all the cafe data.

Using this database and what you learnt about REST APIs and web development, create a website that uses this data.
It should display the cafes, but it could also allow people to 1. add new cafes or 2. delete cafes.

For example, this startup in London has a website that does exactly this:
https://laptopfriendly.co/london
"""
# Tasks
"""
1./Y Display all information
2./Y Connect database/API (instead of using csv import)
3. INTERACT WITH DATABASE UPON USER REQUEST
3.1/Y Add new cafes
3.2/Y Delete cafes

# DATATYPE CASTING- https://stackoverflow.com/questions/14589833/typeerror-argument-of-type-instance-is-not-iterable
"""
# IMPROVEMENTS + NEW FEATURES:
"""
IMPR-A. ADD USER FEATURE - LOGIN/LOGOUT/SIGNUP
IMPR-B. ADD CAFE IMAGE
IMPR-1.Sort cafe according to alphabetical order/ EVEN BETTER ALLOW USERS TO SORT ALL FIELDS BY CLICKING ON COLUMN HEADER
       #SQLAlchemy sort database by column value
IMPR-2.Newline for price entry (too cluttered)
IMPR-3.Implement better solution for dynamic database edit (PATCH) instead of using traditional tedious but proven conditionals
IMPR-4.(FIXED)
      Allow PATCH using add.html with automatically filled form elements (of currently selected attributes)
      (Add input text for user to choose Cafe name/ID) #Flask form input textbox
      (How to fill flask form using data from SQL query?)
      (Flask- How to check where the previous route for redirect URL is from?)
      (Flask- How to send variable from previous route to next route?)
      Flask sessions TypeError: Object of type set is not JSON serializable
      https://flask-session.readthedocs.io/en/latest/
      https://stackoverflow.com/questions/27611216/how-to-pass-a-variable-between-flask-pages
IMPR-5 How to auto update cafe_id after deletion of cafes?
       #auto update database column
IMPR-6 (FIXED) 
        WTForm prepopulate form; Add text to wtform string field parameter
        https://stackoverflow.com/questions/5117479/wtforms-how-to-prepopulate-a-textarea-field
IMPR-7 (FIXED) Delete cafe with button; aft pressing button redirect to enter api-key; if not validated deny access
IMPR-8 (FIXED) Allow updating cafe with button (Instead of typing name)
"""

from flask_sqlalchemy import SQLAlchemy  # Database

from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ABCDEFU'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
Bootstrap(app)

# CREATING DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    cafe_id = db.Column(db.Integer, primary_key=True)

    # 11 entries
    name = db.Column(db.String(250), unique=True, nullable=False)
    open = db.Column(db.String(250), nullable=False)
    close = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)

    toilet = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.String(250), nullable=False)
    wifi_rating = db.Column(db.String(250), nullable=False)
    power = db.Column(db.String(250), nullable=False)
    calls = db.Column(db.String(250), nullable=False)

    coffee_price = db.Column(db.String(250), nullable=False)
    edit_cafe = db.Column(db.String(250), nullable=False)
    delete_cafe = db.Column(db.String(250), nullable=False)
    # url_map = db.Column(db.String(500), nullable=False)
    # url_img = db.Column(db.String(500), nullable=False)


db.create_all()


# How to integrate flask forms with SQLAlchemy?
# Disable autocomplete
# https://stackoverflow.com/questions/49471831/customizing-flask-wtf-or-wtforms
# https://stackoverflow.com/questions/15950774/flask-wtf-passwordfield-disable-autocomplete
class CafeForm(FlaskForm):
    name = StringField(label='Cafe Name', default="Starb*EA*ky", validators=[DataRequired()],
                       render_kw={"autocomplete": "off"})
    open = StringField(label='Opening Time e.g. 6.30AM', default="6.30AM", validators=[DataRequired()],
                       render_kw={"autocomplete": "off"})
    close = StringField(label='Closing Time e.g. 8:30PM', default="8.30PM", validators=[DataRequired()],
                        render_kw={"autocomplete": "off"})
    location = StringField(label='Cafe location on Google Maps (URL)', default="https://www.starbucks.com.sg",
                           validators=[DataRequired(), URL()],
                           render_kw={"autocomplete": "off"})
    seats = SelectField(label='# of chairs 🪑?',
                        choices=("🪑<5", "6<🪑<10", "11<🪑<20", "21<🪑<30", "31<🪑<50", "51<🪑<100"),
                        validators=[DataRequired()])

    toilet = SelectField(label='# of washrooms 🚽?', choices=("✘", "🚽=1", "🚽=2", "🚽=3", "🚽=4", "🚽>=5"),
                         validators=[DataRequired()])
    rating = SelectField(label='Coffee Rating', choices=("☕", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"),
                         validators=[DataRequired()])
    wifi_rating = SelectField(label='Wifi Strength Rating',
                              choices=("✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"),
                              validators=[DataRequired()])
    power = SelectField(label='Power Socket Availability',
                        choices=("✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"), validators=[DataRequired()])
    calls = SelectField(label='In-built phones booths/call zone?', choices=("✘", "Y"), validators=[DataRequired()])

    coffee_price = SelectField(label='Coffee Price', choices=(
        "☕<=1.00$", "1.01$<☕<2.00$", "2.01<☕<3.00$", "3.01<☕<4.00$", "4.01<☕<5.00$", "Middle Class: 5.01<☕<6.00$",
        "High Class: 6.01<☕<10.00$", "Premium: 10.01<☕<15.00$", "Ultra Premium: ☕>15.00$"), validators=[DataRequired()])
    # Flask form- Why cannot have linebreak in data entry \n?
    # https://stackoverflow.com/questions/12244057/any-way-to-add-a-new-line-from-a-string-with-the-n-character-in-flask
    # HTML/WTForm linebreak

    """
<!--                        {% elif ("Class" or "Premium" ) in (cafes[i][j]) %}-->
<!--                            {{cafe_pricing = cafes[i][j].split(":")}}-->
<!--                            {{word = cafe_pricing[0]}}-->
<!--                            {{price = cafe_pricing[1]}}-->
<!--				            <th scope="row" class="col-lg-1" > {{word}}:<br/>{{price}} </th>-->
    """
    submit = SubmitField(label='Submit')


@app.route("/")
def home():
    return render_template("index.html")


# DISPLAY ALL CAFES
# HTML table display full length of data (change css table-layout)
# SQLAlchemy access database item as python dictionary (convert to)
# https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
# HOW TO SORT ACCORDING TO DESIRED COLUMN ORDER?
# ENDED UP JUST QUERYING EVERYTHING MANUALLY AND SETTING CUSTOM DISPLAY NAMES FOR CAFE ATTRIBUTES
# Sort in python instead of SQLAlchemy. Map database in order before displaying on website
# SQLAlchemy display database item in column order/ order database item /SQLAlchemy mapping?
# SQLAlchemy changing/set database column name /query by column

@app.route('/cafes', methods=["GET"])
def all_cafes():
    # Creating cafe attribute display names
    cafe_attributes = ["EDIT?", "Name of cafe", "Website", "Wifi", "Rating", "Coffee Price S$",
                       "Seats", "Power", "Calls", "Opening Hours", "Closing Hours",
                       "Toilet", "DELETE?"]
    # cafes returned as list
    cafes = db.session.query(Cafe.edit_cafe, Cafe.name, Cafe.location, Cafe.wifi_rating, Cafe.rating, Cafe.coffee_price,
                             Cafe.seats, Cafe.power, Cafe.calls, Cafe.open, Cafe.close,
                             Cafe.toilet, Cafe.delete_cafe).all()
    print(cafes)

    cafe_names = db.session.query(Cafe.name).all()
    print(cafe_names)
    # #Original method -- unsorted columns (dictionary)
    # # cafe_order = ["name","open","close","location","seats",
    # #               "toilet","rating","wifi_rating","power","calls",
    # #               "coffee_price"]
    # cafes = db.session.query(Cafe).all()
    # cafe_database=[cafe.__dict__ for cafe in cafes]
    # #TESTING CAFE - Displaying all cafe data & changing url to a clickable link
    # for i in range(len(cafe_database)):
    #     for item in cafe_database[i]:
    #         if "http" in str(cafe_database[i][f"{item}"]):
    #             print("=============================")
    #             print("CHANGED TO URL")
    #             print("MAP LINKS")
    #             print(cafe_database[i]["location"])
    #             print("=============================")
    #         else:
    #             print(cafe_database[i][f"{item}"])
    # # return render_template('cafes.html', cafes=cafe_database, cafe_attr=cafe_attributes)

    """
    ------------------------------cafes.html : displaying all cafes (originally dictionary)-----------------------------
            <thead>
            <tr>
              {% for item in cafes[0] %}
                {% if "sqlalchemy.orm" in (cafes[0][item])|string %}
                    {{continue}}
                {% else %}
                    <th scope="col">{{item}}</th>
                {% endif %}
              {% endfor %}
            </tr>
          </thead>

          <tbody>

           {% for i in range(cafes|length) %}
            <tr>
              {% for item in cafes[i] %}
                {% if "sqlalchemy.orm" in (cafes[i][item])|string %}
                    {{continue}}
                {% elif item|string == "cafe_id"  %}
                    {{continue}}
                {% elif "http" in (cafes[i][item])|string %}
                    <th><a href="{{cafes[i][item]}}">Maps Link</a></th>
                {% else %}
                    <th scope="col">{{cafes[i][item]}}</th>
                {% endif %}
              {% endfor %}

              {% endfor %}

            </tr>
          </tbody>
    """

    # for item in cafe_order:
    #     db.session.query(Cafe).item

    # for cafe in cafes:
    #     print(cafe.__dict__)

    # print("CAFE DATABASE 1ST ITEM")
    # for item in cafe_database[0]:
    #     print(item)
    #     print(cafe_database[0][f"{item}"])
    return render_template('cafes.html', cafes=cafes, cafe_attr=cafe_attributes)


@app.route('/add/<int:cafe_to_update_id>', methods=["GET", "POST", "PATCH"])
# ALLOWS USER TO ADD NEW CAFE (INTERACTION WITH CAFE DATABASE)
def add_cafe(cafe_to_update_id):
    cafe_to_update = Cafe.query.get(cafe_to_update_id)
    print(f"cafe_to_update: {cafe_to_update}")
    try:
        flash(f"Cafe request processing : {cafe_to_update.name}")
    except AttributeError:
        flash(f"Adding new cafe ☕")

    try:
        # # PRE-POPULATE CAFE DETAILS (originally in update_cafe but cannot send object over to add_cafe)
        update_cafe_form = CafeForm(
            name=cafe_to_update.name,
            open=cafe_to_update.open,
            close=cafe_to_update.close,
            location=cafe_to_update.location,
            seats=cafe_to_update.seats,

            toilet=cafe_to_update.toilet,
            rating=cafe_to_update.rating,
            wifi_rating=cafe_to_update.wifi_rating,
            power=cafe_to_update.power,
            calls=cafe_to_update.calls,

            coffee_price=cafe_to_update.coffee_price,
            edit_cafe=cafe_to_update.name,
            delete_cafe=cafe_to_update.name
        )
        form = update_cafe_form
    except AttributeError:  # link from index.html uses cafe_to_update_id=0
        form = CafeForm()
    # session["update_cafe_form"] = json.dumps(update_cafe_form)
    # form = session.get("update_cafe_form",None)

    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get("name"),
            open=request.form.get("open"),
            close=request.form.get("close"),
            location=request.form.get("location"),
            seats=request.form.get("seats"),

            toilet=request.form.get("toilet"),
            rating=request.form.get("rating"),
            wifi_rating=request.form.get("wifi_rating"),
            power=request.form.get("power"),
            calls=request.form.get("calls"),

            coffee_price=request.form.get("coffee_price"),
            edit_cafe=request.form.get("name"),
            delete_cafe=request.form.get("name")
            # Have to use name as temporary ref bcos Cafe.cafe_id for 1st item is not defined
            # But how to send correct url for deleting cafe (for every cafe in loop)?
            # Send name to delete route; then compute Cafe.cafe_id (Too complicated to do calcs in HTML file; annoying syntax + messy)
        )
        cafe_names = db.session.query(Cafe.name).all()
        print(cafe_names)
        print(new_cafe.name)
        cafe_names_ = []
        for item in cafe_names:
            cafe_names_.append(item[0])
        print(cafe_names_)
        # IF DIRECTED FROM UPDATE PAGE, LOAD RELEVANT DATA FOR USER TO EDIT & SUBMIT
        if new_cafe.name in cafe_names_:
            print("Updating database")
            print(new_cafe.name)
            # SQLAlchemy how to PATCH multiple values?
            # EASY SOLUTION--- JUST DELETE OLD COPY AND ADD NEW COPY
            db.session.delete(cafe_to_update)
            db.session.commit()
            print("Cafe deleted")
            db.session.add(new_cafe)
            db.session.commit()
            # return jsonify(response={"success": f"Successfully edited {new_cafe.name}."})
            return redirect(url_for('all_cafes'))
        # ELSE CREATE NEW CAFE ENTRY
        else:
            db.session.add(new_cafe)
            db.session.commit()
            # return jsonify(response={"success": "Successfully added the new cafe."})
            return redirect(url_for('all_cafes'))
    else:
        print("NOT SUBMITTED")
    return render_template('add.html', form=form)


class CafeUpdate(FlaskForm):
    name = StringField('Cafe Name?', validators=[DataRequired()], render_kw={"autocomplete": "off"})
    submit = SubmitField(label='Submit')


@app.route("/update/<edit_link_name>", methods=["GET", "PATCH", "POST"])
def update_cafe_details(edit_link_name):
    # ---------ADDING UPDATE PAGE & LOADING ALL RELEVANT CAFE DETAILS AFTER USER CHOSEN A CAFE--------#
    try:
        update_form = CafeUpdate(
            name=edit_link_name
        )
    except AttributeError:
        update_form = CafeUpdate()
    error = None
    if update_form.validate_on_submit():
        try:
            update_cafe = Cafe(
                name=request.form.get("name"),
            )
            cafe_name = update_cafe.name
            print(f"cafe_name : {cafe_name}")
            cafe_to_update = Cafe.query.filter_by(name=cafe_name).first()
            print(f"cafe_to_update : {cafe_to_update}")
            cafe_to_update_id = cafe_to_update.cafe_id
            print(f"cafe_to_update_id: {cafe_to_update_id}")

            # return jsonify(response={"success": f"Cafe request processing : {update_cafe.name}"})
            return redirect(url_for('add_cafe', cafe_to_update_id=cafe_to_update_id))

        except AttributeError:
            # How to show error message flask? #Flash
            flash("Invalid Cafe Name!")
            return redirect(url_for('update_cafe_details', edit_link_name=edit_link_name))

    return render_template('update.html', update_form=update_form)


# # ALLOWS USERS TO UPDATE ANY CAFE DETAILS
# # Currently can change any fixed variable input but not dynamic user input
# # Example URL route-
# # http://127.0.0.1:5000/update/<int:cafe_id>/<change_cafe_attribute>?cafe_value=STARRYBUGGER
# @app.route("/update/<int:cafe_id>/<change_cafe_attribute>", methods=["GET", "PUT", "PATCH"])
# def update_cafe_details(cafe_id, change_cafe_attribute):
#     # cafe_attribute = str(request.args.get("change_cafe_attribute"))
#     # print(f"cafe_attribute: {cafe_attribute}")
#     cafe_value = request.args.get("cafe_value")
#     print(f"cafe_value: {cafe_value}")
#     cafe = db.session.query(Cafe).get(cafe_id)
#     print(cafe.name)
#     print(cafe.coffee_price)
#     if cafe:
#         # HOW TO QUERY FOR ALL COLUMNS IN DATABASE? How to check all column names in sqlalchemy?
#         # https://stackoverflow.com/questions/6039342/how-to-print-all-columns-in-sqlalchemy-orm
#         # HOW TO CHECK IF PARTICULAR VALUE IS A COLUMN IN DATABASE?
#
#         # (No wonder u got stuck trying to send cafe_attribute as parameter with key-value pairs. Should have just send it to function input by getting intended variable from route)
#         # Still cant send...
#         from sqlalchemy import inspect
#         inst = inspect(Cafe)
#         attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
#
#         """1.THE VARIABLE change_cafe_attribute MATCHES COLUMN NAME EXACTLY BUT SIMPLY JUST CANNOT USE IT IN cafe.change_cafe_attribute= cafe_value TO UPDATE CAFE DETAILS"""
#         if change_cafe_attribute in attr_names:
#             # attribute_to_change = db.session.query(Cafe.change_cafe_attribute)
#             # print(attribute_to_change)
#             print(attr_names)
#             print(f"cafe: {cafe}")
#             print(change_cafe_attribute)
#             # print(f'cafe.cafe_attribute: {cafe[f"{cafe_attribute}"]}')
#
#             """THE PROBLEM IS IN ASSIGNING VALUE TO CHOSEN COLUMN - CANT SEEM TO SET cafe_attribute TO THE RESPECTIVE COLUMN NAME TO CHANGE ITS VALUE"""
#             # SQLALCHEMY HOW TO CHECK FOR DYNAMIC USER INPUT AND EDIT VALUE
#             # selecting database column sqlalchemy & changing its value
#             # https://stackoverflow.com/questions/6977658/sqlalchemy-selecting-which-columns-of-an-object-in-a-query
#             # https://stackoverflow.com/questions/11918857/how-to-select-only-some-columns-in-sqlalchemy
#             # https://stackoverflow.com/questions/9667138/how-to-update-sqlalchemy-row-entry
#
#             # from sqlalchemy import select
#             # results = select([Cafe.c.change_cafe_attribute])
#
#             """But works if a column name is specifically set """
#             # cafe.coffee_price = cafe_value
#             # cafe.change_cafe_attribute = cafe_value
#
#             """2. WORKAROUND: ITERATE THROUGH A LIST OF CAFE ATTRIBUTES THEN USE INDEX i TO REFERENCE COLUMN NAME"""
#             # cafe_database_attr = ["name","open","close","location","seats",
#             #               "toilet","rating","wifi_rating","power","calls",
#             #               "coffee_price"]
#             # for i in range(len(cafe_database_attr)):
#             #     if str(cafe_database_attr[i]) == str(change_cafe_attribute):
#             #         print("TRYING TO ACCESS COFFEE DATABASE")
#             #         print(cafe_database_attr[i])
#             #         print(cafe.cafe_database_attr[i])
#             # ALREADY SET VARIABLE TO THE EXACT COLUMN NAME; STILL SAME PROBLEM; SQLALCHEMY LIMITATION? How come it works for cafe_id but not any other randomly chosen column name?
#             #         cafe.cafe_database_attr[i] = cafe_value #
#             #         db.session.commit()
#             #         print(cafe.cafe_database_attr[i])
#
#             """3. NO CHOICE BUT TO USE TEDIOUS YET PROVEN CONDITIONALS FOR EACH SINGLE COLUMN x11 - SINCE SQLALCHEMY SYNTAX DOESNT ACCEPT ASSIGNMENTS EVEN IF ITS THE EXACT SAME VARIABLE!@!!@#@!$@!@"""
#             if change_cafe_attribute == "name":
#                 cafe.name = cafe_value
#                 print(f"3 {cafe}")
#                 print(type(cafe))
#                 # print(f"3. {cafe.c.change_cafe_attribute}")
#             elif change_cafe_attribute == "open":
#                 cafe.open = cafe_value
#             elif change_cafe_attribute == "close":
#                 cafe.close = cafe_value
#             elif change_cafe_attribute == "location":
#                 cafe.location = cafe_value
#             elif change_cafe_attribute == "seats":
#                 cafe.seats = cafe_value
#             elif change_cafe_attribute == "toilet":
#                 cafe.toilet = cafe_value
#             elif change_cafe_attribute == "rating":
#                 cafe.rating = cafe_value
#             elif change_cafe_attribute == "wifi_rating":
#                 cafe.wifi_rating = cafe_value
#             elif change_cafe_attribute == "power":
#                 cafe.power = cafe_value
#             elif change_cafe_attribute == "calls":
#                 cafe.calls = cafe_value
#             elif change_cafe_attribute == "coffee_price":
#                 cafe.coffee_price = cafe_value
#             db.session.commit()
#             # print(f'cafe.cafe_attribute: {cafe[f"{cafe_attribute}"]}')
#
#             return jsonify(response={
#                 "success": f"Successfully updated {cafe_id} cafe's {change_cafe_attribute} to ...\nPlease reload the page to verify changes!"})
#         else:
#             return jsonify(response={"failure": f"Cafe has id {cafe_id} but cafe_attribute not found"})
#     else:
#         return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})

class CafeDelete(FlaskForm):
    password = StringField('ENTER YOUR PASSWORD?', default="$COFFEE$", validators=[DataRequired()],
                           render_kw={"autocomplete": "off"})
    submit = SubmitField(label='Submit')


@app.route("/delete-caffeys/<name>", methods=["GET", "POST", "DELETE"])
# Example URL route-
# http://127.0.0.1:5000/delete-caffeys/<int:cafe_id>?api-key=TopSecretAPIKey
# ALLOWS USER TO DELETE NEW CAFE (INTERACTION WITH CAFE DATABASE)
# Requires GET request otherwise method not allowed

def delete_cafe(name):
    cafe_to_delete = Cafe.query.filter_by(name=name).first()
    print(f"cafe_to_delete : {cafe_to_delete}")
    cafe_id = cafe_to_delete.cafe_id
    print(f"cafe delete id: {cafe_id}")

    delete_form = CafeDelete()
    if delete_form.validate_on_submit():
        api_key = request.form.get("password")
        print(api_key)
        # print(request.args.get("api-key"))
        # api_key = request.args.get("api-key")

        # Check for access validation
        if api_key == "$COFFEE$":
            cafe = db.session.query(Cafe).get(cafe_id)
            print(cafe.cafe_id)
            if cafe:
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(response={"Success": "Successfully deleted the cafe from the database."}), 200
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            return jsonify(
                error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

    return render_template('delete.html', delete_form=delete_form)


@app.route("/essentials")
def essential_c():
    return render_template('essentials.html')


if __name__ == '__main__':
    app.run(debug=True)
