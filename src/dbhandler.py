from werkzeug.datastructures import ImmutableMultiDict
import sqlite3


def add_vote_record(db: sqlite3.Connection, form: ImmutableMultiDict, cookies: ImmutableMultiDict, language: str = 'en'):
    """
    Add or update a vote record with language tracking.
    If user has voted before (has vote_id cookie), updates their existing vote.
    Otherwise creates a new vote record.
    """
    print(form)
    qr_id = form['qr_id']
    taiwan = form['response']

    cur = db.cursor()
    cur.execute("select IFNULL(MAX(seq), 0) from sqlite_sequence where name=?", ('vote2qr',))
    (row,) = cur.fetchone()

    # TODO: error handling if cookie is not valid int
    vote_id = int(cookies.get('vote_id', default=str(row + 1)))

    cur.execute(
        "INSERT INTO vote2qr (id, response, qr_id, language) VALUES (?, ?, ?, ?) "
        "ON CONFLICT DO UPDATE SET response = ?, qr_id = ?, language = ?;",
        (vote_id, taiwan, qr_id, language, taiwan, qr_id, language)
    )
    cur.close()
    db.commit()

    return vote_id


def add_loc_record(db: sqlite3.Connection, form: ImmutableMultiDict):
    """Add location record - internal use only."""
    print(form)
    lat = form['lat']
    lng = form['lng']
    qr_id = form['qr_id']
    print(lat, lng, qr_id)


def add_email_record(db: sqlite3.Connection, form: ImmutableMultiDict, cookies: ImmutableMultiDict, language: str = 'en'):
    """
    Basic insertion of email signups with language tracking.
    Minimal validation: non-empty and contains '@'.
    Associates the email with vote_id if cookie 'vote_id' exists and is an int.
    """
    email = form.get('email', '').strip()
    if not email or '@' not in email:
        return None

    vote_id = cookies.get('vote_id')
    try:
        vote_id_int = int(vote_id) if vote_id is not None else None
    except Exception:
        vote_id_int = None

    cur = db.cursor()
    cur.execute(
        "INSERT INTO email_signups (email, vote_id, language) VALUES (?, ?, ?);", 
        (email, vote_id_int, language)
    )
    last_id = cur.lastrowid
    db.commit()
    cur.close()
    return last_id