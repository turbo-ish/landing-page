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


def add_sports_records(db: sqlite3.Connection, form: ImmutableMultiDict, cookies: ImmutableMultiDict, language: str = 'en'):
    """
    Save selected sports to database.
    Handles both predefined sports (checkboxes) and custom sports (text field).
    Associates sports with vote_id from cookies.
    
    OVERWRITES any existing sports for this vote_id (clears old selections first).
    """
    vote_id = cookies.get('vote_id')
    try:
        vote_id_int = int(vote_id) if vote_id is not None else None
    except Exception:
        vote_id_int = None
    
    if vote_id_int is None:
        return None
    
    cur = db.cursor()
    
    # Delete all existing sports for this vote_id (prevents duplicates on re-voting)
    cur.execute("DELETE FROM user_sports WHERE vote_id = ?;", (vote_id_int,))
    
    # Get all selected sports from checkboxes
    selected_sports = form.getlist('sports')
    
    # Insert each selected predefined sport
    for sport in selected_sports:
        if sport.strip():
            cur.execute(
                "INSERT INTO user_sports (vote_id, sport, is_custom, language) VALUES (?, ?, ?, ?);",
                (vote_id_int, sport.strip(), False, language)
            )
    
    # Get custom sport from text field
    custom_sport = form.get('custom_sport', '').strip()
    if custom_sport:
        cur.execute(
            "INSERT INTO user_sports (vote_id, sport, is_custom, language) VALUES (?, ?, ?, ?);",
            (vote_id_int, custom_sport, True, language)
        )
    
    db.commit()
    cur.close()
    
    return vote_id_int