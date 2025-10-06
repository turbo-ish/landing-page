import base64
import sqlite3
from io import BytesIO
import os

from flask import Flask, render_template, request, make_response, redirect, url_for
from markupsafe import Markup
from qrcode.main import make
import qrcode
import qrcode.image.svg
from xml.dom.minidom import parse, parseString
from werkzeug.utils import send_file

from dbhandler import add_vote_record, add_loc_record, add_email_record
from qr_svg import make_qr_border_svg #pls no "from src.qr_svg" or will break on server
from src.flyer.flyer_generator import create_flyer

if os.environ.get('RUNNING_IN_DOCKER'):
    # Docker path - uses the volume mount
    DB_PATH = '/app/data/myfuckingdb.db'
else:
    # Local development path - goes up one level from src/
    DB_PATH = '../myfuckingdb.db'

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY AUTOINCREMENT, lat FLOAT, lng FLOAT);")
cur.execute("CREATE TABLE IF NOT EXISTS vote2qr (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, qr_id INTEGER);")
cur.execute("CREATE TABLE IF NOT EXISTS email_signups (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, vote_id INTEGER);")
cur.close()


app = Flask(__name__)


@app.route('/thank_you')
def thanks():
    return render_template('thank_you.html', show_email = request.cookies['show_email_form'])

@app.route('/loc')
def set_loc():
    return render_template('set_qr_loc.html')


@app.route("/<int:qr_id>", methods=['GET', 'POST'])
def landing(qr_id: int):
    if request.method == 'POST':
        # Handle the vote submission
        vote_id = add_vote_record(db, request.form, request.cookies)

        resp_val = (request.form.get('response') or '').strip().lower()
        show_email = '1' if resp_val in ('yes') else '0'
        
        # Create redirect response
        resp = make_response(redirect('/thank_you'))
        resp.set_cookie('vote_id', str(vote_id))
        resp.set_cookie('show_email_form', show_email)

        return resp
    
    # Handle GET request - show the voting form
    return render_template('landing.html', qr_id=qr_id)

@app.route('/<int:qr_id>/qr', methods=['GET'])
def gen_qrcode(qr_id: int):
    img_svg = make_qr_border_svg(qr_id)

    return render_template("qr.html", svg=Markup(img_svg))

@app.route('/<lang>/<int:qr_id>/flyer', methods=['GET'])
def gen_flyer(lang: str, qr_id: int):
    img_svg = create_flyer(lang=lang, qr_id=qr_id)

    return render_template("qr.html", svg=Markup(img_svg))

@app.route("/setqrloc", methods=['GET', 'POST'])
def set_qr_loc():
    if request.method == 'POST':
        add_loc_record(db, request.form)

    return render_template('set_qr_loc.html')

@app.route('/save_email', methods=['POST'])
def save_email():
    # save posted email; vote_id (if available) is read from cookies inside add_email_record
    add_email_record(db, request.form, request.cookies)
    resp = make_response(redirect(url_for('thanks')))
    resp.set_cookie('show_email_form', '0')
    return resp


if __name__ == '__main__':

    app.run(host="127.0.0.1", port=8000, debug=True)