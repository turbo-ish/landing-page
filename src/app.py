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
from translations import get_text, is_valid_lang, get_default_lang

if os.environ.get('RUNNING_IN_DOCKER'):
    DB_PATH = '/app/data/myfuckingdb.db'
else:
    DB_PATH = '../myfuckingdb.db'

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY AUTOINCREMENT, lat FLOAT, lng FLOAT);")
cur.execute("CREATE TABLE IF NOT EXISTS vote2qr (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, qr_id INTEGER, language TEXT);")
cur.execute("CREATE TABLE IF NOT EXISTS email_signups (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, vote_id INTEGER, language TEXT);")
cur.close()

app = Flask(__name__)


@app.route('/thank_you')
@app.route('/<lang>/thank_you')
def thanks(lang=None):
    """Thank you page with language support."""
    if lang is None or not is_valid_lang(lang):
        lang = request.cookies.get('language', get_default_lang())
    
    show_email = request.cookies.get('show_email_form', '0')
    
    return render_template(
        'thank_you.html', 
        show_email=show_email,
        lang=lang,
        t=lambda key: get_text(lang, key)
    )


@app.route('/loc')
def set_loc():
    """Internal use - no translation needed."""
    return render_template('set_qr_loc.html')


@app.route("/<lang>/<int:qr_id>", methods=['GET', 'POST'])
def landing(lang: str, qr_id: int):
    """Main landing page with language support."""
    print(f"Lang: {lang}")
    print(f"Test translation: {get_text(lang, 'title')}")

    # Validate and normalize language
    if not is_valid_lang(lang):
        # Redirect to default language if invalid
        return redirect(url_for('landing', lang=get_default_lang(), qr_id=qr_id))
    
    if request.method == 'POST':
        # Add language to form data for database storage
        form_data_with_lang = request.form.copy()
        
        # Handle the vote submission
        vote_id = add_vote_record(db, form_data_with_lang, request.cookies, lang)

        resp_val = (request.form.get('response') or '').strip().lower()
        show_email = '1' if resp_val in ('yes') else '0'
        
        # Create redirect response with language
        resp = make_response(redirect(url_for('thanks', lang=lang)))
        resp.set_cookie('vote_id', str(vote_id))
        resp.set_cookie('show_email_form', show_email)
        resp.set_cookie('language', lang)  # Store language preference

        return resp
    
    # Handle GET request - show the voting form
    return render_template(
        'landing.html', 
        qr_id=qr_id,
        lang=lang,
        t=lambda key: get_text(lang, key)
    )


# Legacy route redirect - for backwards compatibility
@app.route("/<int:qr_id>", methods=['GET'])
def landing_no_lang(qr_id: int):
    """Redirect URLs without language to default language."""
    return redirect(url_for('landing', lang=get_default_lang(), qr_id=qr_id))


@app.route('/<int:qr_id>/qr', methods=['GET'])
def gen_qrcode(qr_id: int):
    """Generate QR code - internal use."""
    img_svg = make_qr_border_svg(qr_id)

    root = parseString(img_svg)
    path = root.firstChild.firstChild.toprettyxml()
    print(path)

    return render_template("qr.html", svg=Markup(img_svg))


@app.route("/setqrloc", methods=['GET', 'POST'])
def set_qr_loc():
    """Set QR location - internal use."""
    if request.method == 'POST':
        add_loc_record(db, request.form)

    return render_template('set_qr_loc.html')


@app.route('/save_email', methods=['POST'])
@app.route('/<lang>/save_email', methods=['POST'])
def save_email(lang=None):
    """Save email with language support."""
    if lang is None or not is_valid_lang(lang):
        lang = request.cookies.get('language', get_default_lang())
    
    # Save posted email with language
    add_email_record(db, request.form, request.cookies, lang)
    
    resp = make_response(redirect(url_for('thanks', lang=lang)))
    resp.set_cookie('show_email_form', '0')
    resp.set_cookie('language', lang)
    
    return resp


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)