# Joseph Yusufov, Mudadour Rahman, Alice Ni, David Wang
# SoftDev1 pd2
# Atmosphere
# 2019-12-04

from flask import Flask, render_template, request, session
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import flash
from flask import url_for
import urllib
import json
import random
import csv
import sqlite3
import os
from util import cache
DIR = os.path.dirname(__file__) or '.'
DIR += '/'
# cache.cache()

states = {}
reader = csv.reader(open(DIR + "data/states.csv", "r"))
for row in reader:
#     print(row)
    states[row[0]] = row[1]

IDtoAlpha = {}
reader = csv.reader(open(DIR + "data/id-to-alpha.csv", "r"))
for row in reader:
#     print(row)
    IDtoAlpha[row[0]] = row[1]

AlphaToID = {}
for k, v in IDtoAlpha.items():
    AlphaToID[v] = k

BEA_KEY = ""
with open(DIR + 'keys/BEA_KEY.txt', 'r') as file:
    BEA_KEY = file.read().replace('\n', '')

EIA_KEY = ""
with open(DIR + 'keys/EIA_KEY.txt', 'r') as file:
    EIA_KEY = file.read().replace('\n', '')

CENSUS_KEY = ""
with open(DIR + 'keys/CENSUS_KEY.txt', 'r') as file:
    CENSUS_KEY = file.read().replace('\n', '')

if BEA_KEY == "":
    print("!!! Please enter a valid BEA key into BEA_KEY.txt !!!")
    exit()
if EIA_KEY == "":
    print("!!! Please enter a valid EIA key into EIA_KEY.txt !!!")
    exit()
if CENSUS_KEY == "":
    print("!!! Please enter a valid Census key into CENSUS_KEY.txt !!!")
    exit()

# cache.cache()
app = Flask(__name__)  # create instance of class Flask
app.secret_key = os.urandom(24)


def runsqlcommand(command):
    DB_FILE = DIR + "data.db"
    db = sqlite3.connect(DB_FILE)  # open if file exists, otherwise create
    c = db.cursor()  # facilitate db ops
    c.execute(command)
    if "select" in command.lower():
        return c.fetchall()
    db.commit()  # save changes
    db.close()  # close database



@app.route("/")  # assign following fxn to run when root route requested
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    if "username" in session:
        return redirect("/welcome")
    else:
        return render_template("login.html")


@app.route("/register")
def register():
    if len(request.args) > 0:
        username = request.args["username"]
        password = request.args["password"]
        confirm = request.args["confirm"]
        existence_command = "SELECT * FROM loginfo WHERE username LIKE '{}'".format(
            username)
        names = runsqlcommand(existence_command)
        if len(names) != 0:
            flash("Username already taken")
            return redirect("/register")
        if password != confirm:
            flash("Password and confirmation don't match")
            return redirect("/register")
        else:
            insert_username = "INSERT INTO loginfo VALUES ('{}', '{}')".format(
                username, password)
            runsqlcommand(insert_username)
            flash("Successful registration")
            return redirect("/login")
    if "username" in session:
        return redirect("/welcome")
    else:
        return render_template("register.html")


@app.route("/welcome")
def welcome():
    """ Retrieves and prints data about the United States """
    if "username" in session:
        pop = urllib.request.urlopen("https://api.census.gov/data/2018/pep/population?get=POP&for=us:*&key={}".format(CENSUS_KEY))
        data = [json.loads(pop.read())[1][0]]
        # pov = urllib.request.urlopen("https://api.census.gov/data/timeseries/poverty/saipe?get=NAME,SAEPOVALL_PT&for=us:*&time=2016")
        # data.append(json.loads(pov.read())[1][1])
        co2 = urllib.request.urlopen("https://api.eia.gov/series/?api_key={}&series_id=EMISS.CO2-TOTV-IC-TO-US.A".format(EIA_KEY))
        data.append(json.loads(co2.read())["series"][0]["data"][0][1])
        coal = urllib.request.urlopen("https://api.eia.gov/series/?api_key={}&series_id=COAL.CONS_TOT.US-98.A".format(EIA_KEY))
        data.append(json.loads(coal.read())["series"][0]["data"][0][1])
        pci = urllib.request.urlopen("https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAINC1&GeoFIPS=STATE&LineCode=3&Year=2017&ResultFormat=JSON".format(BEA_KEY))
        data.append(json.loads(pci.read())["BEAAPI"]["Results"]["Data"][0]["DataValue"])
        gdp = urllib.request.urlopen("https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAGDP2N&GeoFIPS=STATE&LineCode=3&Year=2017&Frequency=A&ResultFormat=JSON".format(BEA_KEY))
        data.append(json.loads(gdp.read())["BEAAPI"]["Results"]["Data"][0]["DataValue"])
        pic = "http://flags.ox3.in/svg/us.svg"
        return render_template("welcome.html", population = data[0], emissions = data[1], coal = data[2], pci = data[3], gdp = data[4], flag = pic, username=session['username'])
    else:
        return redirect("/login")


@app.route("/auth")
def auth():
    """ Checks for user in the database and in session """
    command = "SELECT * FROM loginfo WHERE username LIKE '{}'".format(
        request.args["username"])
    pair = runsqlcommand(command)
    print("#######")
    print(pair)
    if len(pair) == 0:
        flash("Username not found")
        return "username not found"
    if pair[0][0] == request.args["username"]:
        if pair[0][1] == request.args["password"]:
            session["username"] = request.args["username"]
            flash("Successfully logged in as: {}".format(session['username']))
            print("HERE")
            return redirect("/welcome")
        flash("Wrong password")
        return redirect("/login")
    flash("Wrong username")
    return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("username")
    flash("Logged out successfully")
    return redirect("/login")


@app.route("/favadder")
def favadder():
    """ Mechanism for the user to add to their favorite states list """
    print(session)
    command = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(session["username"])
    d = runsqlcommand(command)
    if len(d) == 0:
        command = "CREATE TABLE {} (TEXT favstate);".format(session["username"])
        runsqlcommand(command)

    command = "SELECT * FROM {};".format(session['username'])
    d = runsqlcommand(command)
    for member in d:
        if IDtoAlpha[ session['state'] ] in member:
            flash("State is already a favorite")
            return redirect("/lookup")
    command = "INSERT INTO {username} VALUES('{state}')".format(username=session["username"], state=IDtoAlpha[session["state"]])
    print(command)
    runsqlcommand(command)
    toflash = "{} added to favorites".format(IDtoAlpha[session["state"]])
    
    flash(toflash)
    return redirect("/lookup")



@app.route("/lookup")
def lookup():
    """ Form that allows users to choose specific states and view the data """
    if 'username' in session:
        if request.args:
            if request.args["submit"] == "favorite":
                session["state"] = request.args["state"]
                return redirect("/favadder")
            print("\n{}".format(request.args.get('state')))
            alpha = IDtoAlpha[request.args.get('state')]
            print("##########\n{}".format(alpha))
            r = urllib.request.urlopen(
                "https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAINC1&GeoFIPS=STATE&LineCode=3&Year=2017&ResultFormat=JSON".format(BEA_KEY)  # Some API link goes here
            )
            income = json.loads(r.read())

            g = urllib.request.urlopen(
                "https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAGDP2N&GeoFIPS=STATE&LineCode=3&Year=2017&Frequency=A&ResultFormat=JSON".format(BEA_KEY)  # Some API link goes here
            )
            gdp = json.loads(g.read())

            p = urllib.request.urlopen(
                "https://api.eia.gov/series/?api_key={}&series_id=EMISS.CO2-TOTV-TT-TO-{}.A".format(EIA_KEY, alpha)
            )
            co2 = json.loads(p.read())

            c = urllib.request.urlopen(
                "https://api.eia.gov/series/?api_key={}&series_id=COAL.CONS_TOT.{}-98.A".format(EIA_KEY, alpha)
            )

            coal = json.loads(c.read())

            f = "http://flags.ox3.in/svg/us/{}.svg".format(alpha.lower())

            print(f)
            command = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(session["username"])
            d = runsqlcommand(command)
            if len(d) == 0:
                favorites = []
            else:
                command = "SELECT * FROM {};".format(session['username'])
                d = runsqlcommand(command)
                favorites = d
                print("FAVORITE STATES: {}".format(favorites))

            return render_template("lookup.html", income=income['BEAAPI']['Results']['Data'][int(request.args.get('state'))], gdp=gdp['BEAAPI']['Results']['Data'][(int(request.args.get('state')))], co2=co2, coal=coal, username=session['username'], states=states, flag=f, selected=request.args.get('state'), favorites=favorites, AlphaToID=AlphaToID)

        command = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(session["username"])
        d = runsqlcommand(command)
        if len(d) == 0:
            favorites = []
        else:
            command = "SELECT * FROM {};".format(session['username'])
            d = runsqlcommand(command)
            favorites = d
            print("FAVORITE STATES: {}".format(favorites))

        return render_template("lookup.html", username=session['username'], states=states, favorites = favorites, AlphaToID=AlphaToID)
    flash("Log in to use Atmo.")
    return redirect("/login")


@app.route("/analysis")
def analysis():
    """ Choosing an independent and dependent variable for comparison """
    if 'username' in session:
        if request.args:
            params = [request.args.get('xVar'), request.args.get('yVar')]
            with open(DIR + "data/JSON/cache.json", "r") as cachefile:
                cache = json.load(cachefile)
            data = {}

            data['x'] = cache[params[0]]
            for member in data['x']['data']:
                data['x']['data'][member] = str(data['x']['data'][member]).replace(',', '')

            data['y'] = cache[params[1]]
            for member in data['y']['data']:
                data['y']['data'][member] = str(data['y']['data'][member]).replace(',', '')

            return render_template("analysis.html", username=session['username'], data=data)
        return render_template("analysis.html", username=session['username'])
    flash("Log in to use Atmo.")
    return redirect("/login")



if __name__ == "__main__":
    app.debug = True
    cache.cache()
    app.run(host='0.0.0.0')
