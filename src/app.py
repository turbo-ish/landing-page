import os
import sqlite3
from xml.dom.minidom import parseString

from flask import Flask, render_template, request, make_response, redirect, url_for
from markupsafe import Markup

from dbhandler import add_vote_record, add_loc_record, add_email_record, add_sports_records
from qr_svg import make_qr_border_svg  # pls no "from src.qr_svg" or will break on server
from translations import get_text, get_sports_list, is_valid_lang, get_default_lang
from flyer.flyer_generator import create_flyer

if os.environ.get('RUNNING_IN_DOCKER'):
    DB_PATH = '/app/data/myfuckingdb.db'
else:
    DB_PATH = '../myfuckingdb.db'

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY AUTOINCREMENT, lat FLOAT, lng FLOAT);")
cur.execute("CREATE TABLE IF NOT EXISTS vote2qr (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, qr_id INTEGER, language TEXT);")
cur.execute("CREATE TABLE IF NOT EXISTS email_signups (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, vote_id INTEGER, language TEXT);")
cur.execute("CREATE TABLE IF NOT EXISTS user_sports (id INTEGER PRIMARY KEY AUTOINCREMENT, vote_id INTEGER, sport TEXT, is_custom BOOLEAN, language TEXT);")
cur.close()

app = Flask(__name__)


@app.route('/')
def index():
    """Redirect base URL to default landing page (QR #500)."""
    return redirect(url_for('landing', lang=get_default_lang(), qr_id=500))


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
        
        # If user said "yes", redirect to sports selection
        if resp_val == 'yes':
            resp = make_response(redirect(url_for('sports_selection', lang=lang)))
            resp.set_cookie('vote_id', str(vote_id))
            resp.set_cookie('language', lang)
            return resp
        else:
            # If "no", go straight to thank you without email form
            resp = make_response(redirect(url_for('thanks', lang=lang)))
            resp.set_cookie('vote_id', str(vote_id))
            resp.set_cookie('show_email_form', '0')
            resp.set_cookie('language', lang)
            return resp
    
    # Handle GET request - show the voting form
    return render_template(
        'landing.html',
        qr_id=qr_id,
        lang=lang,
        t=lambda key: get_text(lang, key)
    )


@app.route('/<lang>/sports', methods=['GET'])
def sports_selection(lang):
    """Sports selection page - shown after user clicks 'Yes'."""
    if not is_valid_lang(lang):
        lang = get_default_lang()

    # Get sports list for the selected language
    sports_list = get_sports_list(lang)

    return render_template(
        'sports_selection.html',
        lang=lang,
        sports_list=sports_list,
        t=lambda key: get_text(lang, key)
    )


@app.route('/<lang>/save_sports', methods=['POST'])
def save_sports(lang):
    """Save selected sports to database."""
    if not is_valid_lang(lang):
        lang = request.cookies.get('language', get_default_lang())

    # Save sports selections
    add_sports_records(db, request.form, request.cookies, lang)

    # Redirect to thank you page with email form
    resp = make_response(redirect(url_for('thanks', lang=lang)))
    resp.set_cookie('show_email_form', '1')
    resp.set_cookie('language', lang)

    return resp


# Legacy route redirect - for backwards compatibility
@app.route("/<int:qr_id>", methods=['GET'])
def landing_no_lang(qr_id: int):
    """Redirect URLs without language to default language."""
    return redirect(url_for('landing', lang=get_default_lang(), qr_id=qr_id))


@app.route('/<lang>/<int:qr_id>/qr', methods=['GET'])
def gen_qrcode(lang: str, qr_id: int):
    """Generate QR code - internal use."""

    if lang == 'nl':
        img_svg = make_qr_border_svg(qr_id=qr_id, top_text="movetogether.now", bottom_text="SCAN MIJ · GA NU SPORTEN",
                                     lang=lang)
    else:
        img_svg = make_qr_border_svg(qr_id, top_text="movetogether.now", bottom_text="SCAN ME · DO SPORTS NOW", lang=lang)

    return render_template("qr.html", svg=Markup(img_svg))


@app.route('/<lang>/<int:qr_id>/flyer', methods=['GET'])
def gen_flyer(lang: str, qr_id: int):
    img_svg = create_flyer(lang=lang, qr_id=qr_id)

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