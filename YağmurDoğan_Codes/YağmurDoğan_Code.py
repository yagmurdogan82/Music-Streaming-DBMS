import sqlite3
import streamlit as st
from datetime import datetime

DB_PATH = "music_streaming.db"

# ---------------- DB HELPERS ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- INIT / SCHEMA ----------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # create tables if not exist (ER diagram compliant)
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS Artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        country TEXT,
        genre TEXT
    );

    CREATE TABLE IF NOT EXISTS ArtistSocialLinks (
        social_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id INTEGER,
        platform TEXT,
        social_link TEXT,
        FOREIGN KEY(artist_id) REFERENCES Artists(artist_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Albums (
        album_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist_id INTEGER,
        release_year INTEGER,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Tracks (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_title TEXT NOT NULL,
        duration_seconds INTEGER,
        album_id INTEGER,
        track_genre TEXT,
        FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS TrackMoods (
        mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER,
        mood TEXT,
        FOREIGN KEY(track_id) REFERENCES Tracks(track_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        f_name TEXT,
        l_name TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS Premium (
        user_id INTEGER PRIMARY KEY,
        renewal_date TEXT,
        payment_method TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Free (
        user_id INTEGER PRIMARY KEY,
        ad_frequency INTEGER,
        listening_limit INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Playlists (
        playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_title TEXT NOT NULL,
        user_id INTEGER,
        creation_date TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS PlaylistTracks (
        playlist_id INTEGER,
        track_id INTEGER,
        position INTEGER,
        PRIMARY KEY (playlist_id, track_id),
        FOREIGN KEY (playlist_id) REFERENCES Playlists(playlist_id) ON DELETE CASCADE,
        FOREIGN KEY (track_id) REFERENCES Tracks(track_id) ON DELETE CASCADE
    );
    """)

    # seed only if Artists is empty
    cur.execute("SELECT COUNT(*) as c FROM Artists")
    if cur.fetchone()["c"] == 0:
        seed_data(conn=conn)

    conn.commit()
    conn.close()

def seed_data(conn):
    cur = conn.cursor()

    # Artists
    artists = [
        ("Rammstein", "Germany", "Industrial Metal"),
        ("Justin Bieber", "USA", "R&B"),
        ("Sezen Aksu", "Turkey", "Pop"),
        ("Massive Attack", "UK", "Trip Hop"),
        ("Astrix", "Israel", "Psychedelic")
    ]
    cur.executemany("INSERT INTO Artists (name, country, genre) VALUES (?, ?, ?)", artists)

    # Artist social links
    socials = [
        (1, "Instagram", "@rammstein"),
        (1, "Website", "rammstein.de"),
        (2, "Instagram", "@justinbieber"),
        (3, "Instagram", "@sezenaksu"),
        (4, "YouTube", "massiveattack.com"),
        (5, "SoundCloud", "soundcloud.com/astrix")
    ]
    cur.executemany("INSERT INTO ArtistSocialLinks (artist_id, platform, social_link) VALUES (?, ?, ?)", socials)

    # Albums
    albums = [
        ("Made In Germany 1995-2011", 1, 2011),
        ("Purpose", 2, 2015),
        ("Sen Ağlama", 3, 1984),
        ("Mezzanine", 4, 1998),
        ("He.art", 5, 2016)
    ]
    cur.executemany("INSERT INTO Albums (title, artist_id, release_year) VALUES (?, ?, ?)", albums)

    # Tracks
    tracks = [
        ("Ich Will", 240, 1, "Industrial Metal"),
        ("Company", 208, 2, "R&B"),
        ("Geri Dön", 260, 3, "Pop"),
        ("Angel", 324, 4, "Trip Hop"),
        ("Deep Jungle Walk", 556, 5, "Psychedelic")
    ]
    cur.executemany("INSERT INTO Tracks (track_title, duration_seconds, album_id, track_genre) VALUES (?, ?, ?, ?)", tracks)

    # Track moods (multivalued)
    moods = [
        (1, "Aggressive"), (1, "Energetic"),
        (2, "Melancholic"),
        (3, "Nostalgic"),
        (4, "Dark"), (4, "Hypnotic"),
        (5, "Trippy")
    ]
    cur.executemany("INSERT INTO TrackMoods (track_id, mood) VALUES (?, ?)", moods)

    # Users (f_name, l_name, email)
    users = [
        ("Yağmur", "Doğan", "yagmur@example.com"),
        ("Ali", "Vatansever", "ali@example.com"),
        ("Nehir", "Kara", "nehir@example.com"),
        ("Huseyn", "Terzi", "huseyn@example.com"),
        ("Zeynep", "Sarı", "zeynep@example.com")
    ]
    cur.executemany("INSERT INTO Users (f_name, l_name, email) VALUES (?, ?, ?)", users)

    # Premium (must reference existing user_id)
    premium = [
        (1, "2025-01-01", "Credit Card"),
        (3, "2025-02-03", "Credit Card")
    ]
    cur.executemany("INSERT INTO Premium (user_id, renewal_date, payment_method) VALUES (?, ?, ?)", premium)

    # Free
    free = [
        (2, 5, 100),
        (4, 10, 50),
        (5, 3, 30)
    ]
    cur.executemany("INSERT INTO Free (user_id, ad_frequency, listening_limit) VALUES (?, ?, ?)", free)

    # Playlists
    now = datetime.utcnow().isoformat()
    playlists = [
        ("Chill Vibes", 1, now),
        ("Workout Mix", 2, now),
        ("Study Focus", 1, now),
        ("Turkish Pop", 3, now),
        ("Electro Nights", 4, now)
    ]
    cur.executemany("INSERT INTO Playlists (playlist_title, user_id, creation_date) VALUES (?, ?, ?)", playlists)

    # PlaylistTracks
    playlist_tracks = [
        (1, 1, 1),
        (1, 5, 2),  
        (2, 4, 1),  
        (3, 3, 1),  
        (4, 2, 1)
    ]
    cur.executemany("INSERT INTO PlaylistTracks (playlist_id, track_id, position) VALUES (?, ?, ?)", playlist_tracks)

    conn.commit()

# ---------------- CRUD: Artists & Socials ----------------
def fetch_all(table):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    return rows

# Artists CRUD
def add_artist(name, country, genre):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Artists (name, country, genre) VALUES (?, ?, ?)", (name, country, genre))
    conn.commit()
    conn.close()

def update_artist(artist_id, name, country, genre):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Artists SET name=?, country=?, genre=? WHERE artist_id=?", (name, country, genre, artist_id))
    conn.commit()
    conn.close()

def delete_artist(artist_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Artists WHERE artist_id=?", (artist_id,))
    conn.commit()
    conn.close()

# ArtistSocialLinks CRUD
def add_artist_social(artist_id, platform, social_link):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO ArtistSocialLinks (artist_id, platform, social_link) VALUES (?, ?, ?)", (artist_id, platform, social_link))
    conn.commit()
    conn.close()

def get_all_artist_socials():
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT s.social_id, a.artist_id, a.name AS artist_name, s.platform, s.social_link
        FROM ArtistSocialLinks s
        JOIN Artists a ON s.artist_id = a.artist_id
        ORDER BY a.name
    """).fetchall()
    conn.close()
    return rows

def update_artist_social(social_id, platform, social_link):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE ArtistSocialLinks SET platform=?, social_link=? WHERE social_id=?", (platform, social_link, social_id))
    conn.commit()
    conn.close()

def delete_artist_social(social_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM ArtistSocialLinks WHERE social_id=?", (social_id,))
    conn.commit()
    conn.close()

# ---------------- CRUD: Albums ----------------
def add_album(title, artist_id, release_year):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Albums (title, artist_id, release_year) VALUES (?, ?, ?)", (title, artist_id if artist_id else None, release_year))
    conn.commit()
    conn.close()

def update_album(album_id, title, artist_id, release_year):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Albums SET title=?, artist_id=?, release_year=? WHERE album_id=?", (title, artist_id if artist_id else None, release_year, album_id))
    conn.commit()
    conn.close()

def delete_album(album_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Albums WHERE album_id=?", (album_id,))
    conn.commit()
    conn.close()

# ---------------- CRUD: Tracks & Moods ----------------
def add_track(track_title, duration_seconds, album_id, track_genre):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Tracks (track_title, duration_seconds, album_id, track_genre) VALUES (?, ?, ?, ?)", (track_title, duration_seconds, album_id if album_id else None, track_genre))
    conn.commit()
    conn.close()

def update_track(track_id, track_title, duration_seconds, album_id, track_genre):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Tracks SET track_title=?, duration_seconds=?, album_id=?, track_genre=? WHERE track_id=?", (track_title, duration_seconds, album_id if album_id else None, track_genre, track_id))
    conn.commit()
    conn.close()

def delete_track(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Tracks WHERE track_id=?", (track_id,))
    conn.commit()
    conn.close()

# Track moods CRUD
def add_track_mood(track_id, mood):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO TrackMoods (track_id, mood) VALUES (?, ?)", (track_id, mood))
    conn.commit()
    conn.close()

def get_all_track_moods():
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT m.mood_id, t.track_id, t.track_title, m.mood
        FROM TrackMoods m
        JOIN Tracks t ON m.track_id = t.track_id
        ORDER BY t.track_title
    """).fetchall()
    conn.close()
    return rows

def update_track_mood(mood_id, mood):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE TrackMoods SET mood=? WHERE mood_id=?", (mood, mood_id))
    conn.commit()
    conn.close()

def delete_track_mood(mood_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM TrackMoods WHERE mood_id=?", (mood_id,))
    conn.commit()
    conn.close()

# ---------------- CRUD: Users, Premium, Free ----------------
def add_user(f_name, l_name, email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Users (f_name, l_name, email) VALUES (?, ?, ?)", (f_name, l_name, email))
    conn.commit()
    conn.close()

def get_all_users():
    return fetch_all("Users")

def update_user(user_id, f_name, l_name, email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET f_name=?, l_name=?, email=? WHERE user_id=?", (f_name, l_name, email, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# Premium
def add_premium(user_id, renewal_date, payment_method):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Premium (user_id, renewal_date, payment_method) VALUES (?, ?, ?)", (user_id, renewal_date, payment_method))
    conn.commit()
    conn.close()

def get_all_premium():
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT p.user_id, u.f_name, u.l_name, p.renewal_date, p.payment_method
        FROM Premium p JOIN Users u ON p.user_id = u.user_id
    """).fetchall()
    conn.close()
    return rows

def update_premium(user_id, renewal_date, payment_method):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Premium SET renewal_date=?, payment_method=? WHERE user_id=?", (renewal_date, payment_method, user_id))
    conn.commit()
    conn.close()

def delete_premium(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Premium WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# Free
def add_free(user_id, ad_frequency, listening_limit):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Free (user_id, ad_frequency, listening_limit) VALUES (?, ?, ?)", (user_id, ad_frequency, listening_limit))
    conn.commit()
    conn.close()

def get_all_free():
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT f.user_id, u.f_name, u.l_name, f.ad_frequency, f.listening_limit
        FROM Free f JOIN Users u ON f.user_id = u.user_id
    """).fetchall()
    conn.close()
    return rows

def update_free(user_id, ad_frequency, listening_limit):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Free SET ad_frequency=?, listening_limit=? WHERE user_id=?", (ad_frequency, listening_limit, user_id))
    conn.commit()
    conn.close()

def delete_free(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Free WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ---------------- CRUD: Playlists ----------------
def add_playlist(playlist_title, user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Playlists (playlist_title, user_id, creation_date) VALUES (?, ?, ?)", (playlist_title, user_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def delete_playlist(playlist_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Playlists WHERE playlist_id=?", (playlist_id,))
    conn.commit()
    conn.close()

def add_track_to_playlist(playlist_id, track_id, position):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO PlaylistTracks (playlist_id, track_id, position) VALUES (?, ?, ?)", (playlist_id, track_id, position))
    conn.commit()
    conn.close()

def remove_track_from_playlist(playlist_id, track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM PlaylistTracks WHERE playlist_id=? AND track_id=?", (playlist_id, track_id))
    conn.commit()
    conn.close()

# ---------------- JOINS / HELPERS ----------------
def join_tracks_albums_artists():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT t.track_id, t.track_title, t.duration_seconds, t.track_genre,
           a.album_id, a.title AS album_title, ar.artist_id, ar.name AS artist_name
    FROM Tracks t
    LEFT JOIN Albums a ON t.album_id = a.album_id
    LEFT JOIN Artists ar ON a.artist_id = ar.artist_id
    ORDER BY ar.name, a.release_year
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_playlists_for_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Playlists WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_tracks_in_playlist(playlist_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT pt.position, t.track_id, t.track_title, t.duration_seconds, t.track_genre,
           a.title as album_title, ar.name as artist_name
    FROM PlaylistTracks pt
    JOIN Tracks t ON pt.track_id = t.track_id
    LEFT JOIN Albums a ON t.album_id = a.album_id
    LEFT JOIN Artists ar ON a.artist_id = ar.artist_id
    WHERE pt.playlist_id = ?
    ORDER BY pt.position
    """, (playlist_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Music Streaming CMS (Full CRUD)", layout="wide")
st.title("🎵 Music Streaming Content Management — FULL CRUD")

# initialize DB & seed if needed
init_db()

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Artists",
    "Artist Social Links",
    "Albums",
    "Tracks",
    "Track Moods",
    "Users",
    "Premium Users",
    "Free Users",
    "Playlists",
    "JOIN: Tracks+Albums+Artists"
])

st.sidebar.markdown("**Database:** " + DB_PATH)

# ------- Dashboard -------
if menu == "Dashboard":
    st.header("Dashboard")
    cols = st.columns(5)
    with cols[0]:
        st.metric("Artists", len(fetch_all("Artists")))
    with cols[1]:
        st.metric("Albums", len(fetch_all("Albums")))
    with cols[2]:
        st.metric("Tracks", len(fetch_all("Tracks")))
    with cols[3]:
        st.metric("Users", len(fetch_all("Users")))
    with cols[4]:
        st.metric("Playlists", len(fetch_all("Playlists")))

# ------- ARTISTS (CRUD) -------
elif menu == "Artists":
    st.header("Artists — Add / Update / Delete")
    artists = fetch_all("Artists")
    st.table([dict(a) for a in artists])

    st.subheader("➕ Add New Artist")
    conn = get_conn()
    cur = conn.cursor()
    with st.form("add_artist"):
        name = st.text_input("Name")
        country = st.text_input("Country")
        genre = st.text_input("Genre")
        if st.form_submit_button("Add"):
            if not name.strip():
                st.error("Name required.")
            else:
                try:
                    add_artist(name.strip(), country.strip() or None, genre.strip() or None)
                    st.success("Artist added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    conn.close()

    st.subheader("✏️ Update Artist")
    artists = fetch_all("Artists")
    if artists:
        choice = st.selectbox("Select Artist", options=[(a["artist_id"], a["name"]) for a in artists], format_func=lambda x: x[1])
        artist_id = choice[0]
        orig = [a for a in artists if a["artist_id"] == artist_id][0]
        with st.form("update_artist"):
            new_name = st.text_input("Name", value=orig["name"])
            new_country = st.text_input("Country", value=orig["country"] or "")
            new_genre = st.text_input("Genre", value=orig["genre"] or "")
            if st.form_submit_button("Update"):
                update_artist(artist_id, new_name.strip(), new_country.strip() or None, new_genre.strip() or None)
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete Artist")
    artists = fetch_all("Artists")
    if artists:
        del_choice = st.selectbox("Delete Artist", options=[(a["artist_id"], a["name"]) for a in artists], format_func=lambda x: x[1])
        if st.button("Delete Selected Artist"):
            delete_artist(del_choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- ARTIST SOCIAL LINKS (CRUD) -------
elif menu == "Artist Social Links":
    st.header("Artist Social Links — Add / Update / Delete")
    socials = get_all_artist_socials()
    st.table([dict(s) for s in socials])

    conn = get_conn()
    cur = conn.cursor()
    artists = cur.execute("SELECT artist_id, name FROM Artists ORDER BY name").fetchall()

    st.subheader("➕ Add Social Link")
    if artists:
        with st.form("add_social"):
            artist_choice = st.selectbox("Artist", options=[(a["artist_id"], a["name"]) for a in artists], format_func=lambda x: x[1])
            platform = st.selectbox("Platform", ["Instagram", "Spotify", "YouTube", "Twitter", "Website", "Other"])
            link = st.text_input("Link (handle or url)")
            if st.form_submit_button("Add Social"):
                if not link.strip():
                    st.error("Link required.")
                else:
                    add_artist_social(artist_choice[0], platform, link.strip())
                    st.success("Social link added.")
                    st.rerun()
    else:
        st.info("Please add an artist first.")
    conn.close()

    st.subheader("✏️ Update Social Link")
    socials = get_all_artist_socials()
    if socials:
        up_choice = st.selectbox("Select Social", options=[(s["social_id"], f"{s['artist_name']} — {s['platform']}") for s in socials], format_func=lambda x: x[1])
        sel = [s for s in socials if s["social_id"] == up_choice[0]][0]
        with st.form("update_social"):
            new_platform = st.selectbox("Platform", ["Instagram", "Spotify", "YouTube", "Twitter", "Website", "Other"], index=0)
            new_link = st.text_input("Link", value=sel["social_link"])
            if st.form_submit_button("Update Social"):
                update_artist_social(up_choice[0], new_platform, new_link.strip())
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete Social Link")
    socials = get_all_artist_socials()
    if socials:
        del_choice = st.selectbox("Select to Delete", options=[(s["social_id"], f"{s['artist_name']} — {s['platform']} — {s['social_link']}") for s in socials], format_func=lambda x: x[1])
        if st.button("Delete Social"):
            delete_artist_social(del_choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- ALBUMS (CRUD) -------
elif menu == "Albums":
    st.header("Albums — Add / Update / Delete")
    albums = fetch_all("Albums")
    st.table([dict(a) for a in albums])

    conn = get_conn()
    cur = conn.cursor()
    artists = cur.execute("SELECT artist_id, name FROM Artists ORDER BY name").fetchall()

    st.subheader("➕ Add Album")
    with st.form("add_album"):
        title = st.text_input("Title")
        artist_choice = st.selectbox("Artist (or select None)", options=[(None, "— None / Compilation —")] + [(a["artist_id"], a["name"]) for a in artists], format_func=lambda x: x[1])
        year = st.number_input("Release Year", min_value=1900, max_value=2100, value=datetime.now().year)
        if st.form_submit_button("Add Album"):
            add_album(title.strip() or "Untitled", artist_choice[0], int(year))
            st.success("Album added.")
            st.rerun()
    conn.close()

    st.subheader("✏️ Update Album")
    albums = fetch_all("Albums")
    if albums:
        sel = st.selectbox("Select Album", options=[(a["album_id"], a["title"]) for a in albums], format_func=lambda x: x[1])
        album = [a for a in albums if a["album_id"] == sel[0]][0]
        with st.form("update_album"):
            new_title = st.text_input("Title", value=album["title"])
            # choose artist by id/name
            artists = fetch_all("Artists")
            artist_choice = st.selectbox("Artist", options=[(None, "— None —")] + [(a["artist_id"], a["name"]) for a in artists], index=0, format_func=lambda x: x[1])
            new_year = st.number_input("Release Year", min_value=1900, max_value=2100, value=album["release_year"] or datetime.now().year)
            if st.form_submit_button("Update Album"):
                update_album(album["album_id"], new_title.strip(), artist_choice[0], int(new_year))
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete Album")
    albums = fetch_all("Albums")
    if albums:
        del_choice = st.selectbox("Delete Album", options=[(a["album_id"], a["title"]) for a in albums], format_func=lambda x: x[1])
        if st.button("Delete Selected Album"):
            delete_album(del_choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- TRACKS (CRUD) -------
elif menu == "Tracks":
    st.header("Tracks — Add / Update / Delete")
    tracks = fetch_all("Tracks")
    st.table([dict(t) for t in tracks])

    conn = get_conn()
    cur = conn.cursor()
    albums = cur.execute("SELECT album_id, title FROM Albums ORDER BY title").fetchall()

    st.subheader("➕ Add Track")
    with st.form("add_track"):
        title = st.text_input("Title")
        duration = st.number_input("Duration (seconds)", min_value=1, max_value=10000, value=180)
        album_choice = st.selectbox("Album (or None)", options=[(None, "— None / Single —")] + [(a["album_id"], a["title"]) for a in albums], format_func=lambda x: x[1])
        genre = st.text_input("Genre")
        if st.form_submit_button("Add Track"):
            add_track(title.strip() or "Untitled", int(duration), album_choice[0], genre.strip() or None)
            st.success("Track added.")
            st.rerun()
    conn.close()

    st.subheader("✏️ Update Track")
    tracks = fetch_all("Tracks")
    if tracks:
        sel = st.selectbox("Select Track", options=[(t["track_id"], t["track_title"]) for t in tracks], format_func=lambda x: x[1])
        track = [t for t in tracks if t["track_id"] == sel[0]][0]
        with st.form("update_track"):
            new_title = st.text_input("Title", value=track["track_title"])
            new_dur = st.number_input("Duration (seconds)", min_value=1, max_value=10000, value=track["duration_seconds"] or 180)
            albums = fetch_all("Albums")
            album_choice = st.selectbox("Album", options=[(None, "— None —")] + [(a["album_id"], a["title"]) for a in albums], format_func=lambda x: x[1])
            new_genre = st.text_input("Genre", value=track["track_genre"] or "")
            if st.form_submit_button("Update Track"):
                update_track(track["track_id"], new_title.strip(), int(new_dur), album_choice[0], new_genre.strip() or None)
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete Track")
    tracks = fetch_all("Tracks")
    if tracks:
        del_choice = st.selectbox("Delete Track", options=[(t["track_id"], t["track_title"]) for t in tracks], format_func=lambda x: x[1])
        if st.button("Delete Selected Track"):
            delete_track(del_choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- TRACK MOODS (CRUD) -------
elif menu == "Track Moods":
    st.header("Track Moods — Add / Update / Delete")
    moods = get_all_track_moods()
    st.table([dict(m) for m in moods])

    conn = get_conn()
    cur = conn.cursor()
    tracks = cur.execute("SELECT track_id, track_title FROM Tracks ORDER BY track_title").fetchall()
    conn.close()

    st.subheader("➕ Add Mood")
    if tracks:
        with st.form("add_mood"):
            track_choice = st.selectbox("Track", options=[(t["track_id"], t["track_title"]) for t in tracks], format_func=lambda x: x[1])
            mood = st.text_input("Mood")
            if st.form_submit_button("Add Mood"):
                if mood.strip():
                    add_track_mood(track_choice[0], mood.strip())
                    st.success("Mood added.")
                    st.rerun()
                else:
                    st.error("Mood required.")
    else:
        st.info("Add a track first.")

    st.subheader("✏️ Update Mood")
    moods = get_all_track_moods()
    if moods:
        up_choice = st.selectbox("Select Mood", options=[(m["mood_id"], f"{m['track_title']} — {m['mood']}") for m in moods], format_func=lambda x: x[1])
        sel = [m for m in moods if m["mood_id"] == up_choice[0]][0]
        with st.form("update_mood"):
            new_mood = st.text_input("New Mood", value=sel["mood"])
            if st.form_submit_button("Update Mood"):
                update_track_mood(up_choice[0], new_mood.strip() or sel["mood"])
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete Mood")
    moods = get_all_track_moods()
    if moods:
        del_choice = st.selectbox("Delete Mood", options=[(m["mood_id"], f"{m['track_title']} — {m['mood']}") for m in moods], format_func=lambda x: x[1])
        if st.button("Delete Selected Mood"):
            delete_track_mood(del_choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- USERS (CRUD) -------
elif menu == "Users":
    st.header("Users — Add / Update / Delete")
    users = get_all_users()
    st.table([dict(u) for u in users])

    conn = get_conn()
    cur = conn.cursor()

    st.subheader("➕ Add User")
    with st.form("add_user"):
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        em = st.text_input("Email")
        if st.form_submit_button("Add User"):
            if not fn.strip():
                st.error("First name required.")
            else:
                add_user(fn.strip(), ln.strip() or None, em.strip() or None)
                st.success("User added.")
                st.rerun()

    st.subheader("✏️ Update User")
    users = get_all_users()
    if users:
        sel = st.selectbox("Select User", options=[(u["user_id"], f"{u['f_name']} {u['l_name'] or ''}") for u in users], format_func=lambda x: x[1])
        u = [x for x in users if x["user_id"] == sel[0]][0]
        with st.form("update_user"):
            new_fn = st.text_input("First Name", value=u["f_name"])
            new_ln = st.text_input("Last Name", value=u["l_name"] or "")
            new_em = st.text_input("Email", value=u["email"] or "")
            if st.form_submit_button("Update User"):
                update_user(u["user_id"], new_fn.strip(), new_ln.strip() or None, new_em.strip() or None)
                st.success("Updated.")
                st.rerun()

    st.subheader("🗑️ Delete User")
    users = get_all_users()
    if users:
        del_choice = st.selectbox("Delete User", options=[(u["user_id"], f"{u['f_name']} {u['l_name'] or ''}") for u in users], format_func=lambda x: x[1])
        if st.button("Delete Selected User"):
            delete_user(del_choice[0])
            st.success("Deleted.")
            st.rerun()
    conn.close()

# ------- PREMIUM USERS (CRUD) -------
elif menu == "Premium Users":
    st.header("Premium Users — View / Add / Update / Delete")
    premiums = get_all_premium()
    st.table([dict(p) for p in premiums])

    conn = get_conn()
    cur = conn.cursor()
    # eligible users for Premium (not already Premium)
    eligible = cur.execute("SELECT user_id, f_name, l_name FROM Users WHERE user_id NOT IN (SELECT user_id FROM Premium)").fetchall()
    conn.close()

    st.subheader("➕ Add Premium")
    if eligible:
        with st.form("add_premium"):
            uchoice = st.selectbox("Select User", options=[(e["user_id"], f"{e['f_name']} {e['l_name']}") for e in eligible], format_func=lambda x: x[1])
            renewal = st.date_input("Renewal Date")
            payment = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "PayPal", "Other"])
            if st.form_submit_button("Add Premium"):
                add_premium(uchoice[0], str(renewal), payment)
                st.success("Premium added.")
                st.rerun()
    else:
        st.info("No eligible users for Premium.")

    st.subheader("✏️ Update / Delete Premium")
    premiums = get_all_premium()
    if premiums:
        choice = st.selectbox("Select Premium", options=[(p["user_id"], f"{p['f_name']} {p['l_name']}") for p in premiums], format_func=lambda x: x[1])
        sel = [p for p in premiums if p["user_id"] == choice[0]][0]
        with st.form("update_premium"):
            new_renewal = st.date_input("Renewal Date", value=datetime.fromisoformat(sel["renewal_date"]).date() if sel["renewal_date"] else datetime.utcnow().date())
            new_payment = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "PayPal", "Other"])
            if st.form_submit_button("Update Premium"):
                update_premium(choice[0], str(new_renewal), new_payment)
                st.success("Updated.")
                st.rerun()
        if st.button("Delete Premium"):
            delete_premium(choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- FREE USERS (CRUD) -------
elif menu == "Free Users":
    st.header("Free Users — View / Add / Update / Delete")
    frees = get_all_free()
    st.table([dict(f) for f in frees])

    conn = get_conn()
    cur = conn.cursor()
    eligible = cur.execute("SELECT user_id, f_name, l_name FROM Users WHERE user_id NOT IN (SELECT user_id FROM Free)").fetchall()
    conn.close()

    st.subheader("➕ Add Free")
    if eligible:
        with st.form("add_free"):
            uchoice = st.selectbox("Select User", options=[(e["user_id"], f"{e['f_name']} {e['l_name']}") for e in eligible], format_func=lambda x: x[1])
            ad_freq = st.number_input("Ad Frequency", min_value=0, max_value=100, value=5)
            limit = st.number_input("Listening Limit", min_value=0, max_value=10000, value=100)
            if st.form_submit_button("Add Free"):
                add_free(uchoice[0], int(ad_freq), int(limit))
                st.success("Free added.")
                st.rerun()
    else:
        st.info("No eligible users for Free.")

    st.subheader("✏️ Update / Delete Free")
    frees = get_all_free()
    if frees:
        choice = st.selectbox("Select Free", options=[(f["user_id"], f"{f['f_name']} {f['l_name']}") for f in frees], format_func=lambda x: x[1])
        sel = [f for f in frees if f["user_id"] == choice[0]][0]
        with st.form("update_free"):
            new_ad = st.number_input("Ad Frequency", min_value=0, max_value=100, value=sel["ad_frequency"])
            new_limit = st.number_input("Listening Limit", min_value=0, max_value=10000, value=sel["listening_limit"])
            if st.form_submit_button("Update Free"):
                update_free(choice[0], int(new_ad), int(new_limit))
                st.success("Updated.")
                st.rerun()
        if st.button("Delete Free"):
            delete_free(choice[0])
            st.success("Deleted.")
            st.rerun()

# ------- PLAYLISTS -------
elif menu == "Playlists":
    st.header("Playlists — View / Create / Manage Tracks")
    playlists = fetch_all("Playlists")
    st.table([dict(p) for p in playlists])

    conn = get_conn()
    cur = conn.cursor()
    users = cur.execute("SELECT user_id, f_name, l_name FROM Users ORDER BY f_name").fetchall()
    tracks = cur.execute("SELECT track_id, track_title FROM Tracks ORDER BY track_title").fetchall()
    conn.close()

    st.subheader("➕ Create Playlist")
    if users:
        with st.form("create_playlist"):
            title = st.text_input("Playlist Title")
            user_choice = st.selectbox("User", options=[(u["user_id"], f"{u['f_name']} {u['l_name']}") for u in users], format_func=lambda x: x[1])
            if st.form_submit_button("Create"):
                add_playlist(title.strip() or "Untitled", user_choice[0])
                st.success("Playlist created.")
                st.rerun()
    else:
        st.info("Add users first.")

    st.subheader("➕ Add / Remove Track to Playlist")
    playlists = fetch_all("Playlists")
    if playlists and tracks:
        pl_choice = st.selectbox("Select Playlist", options=[(p["playlist_id"], p["playlist_title"]) for p in playlists], format_func=lambda x: x[1])
        t_choice = st.selectbox("Select Track", options=[(t["track_id"], t["track_title"]) for t in tracks], format_func=lambda x: x[1])
        pos = st.number_input("Position", min_value=1, max_value=1000, value=1)
        if st.button("Add Track to Playlist"):
            add_track_to_playlist(pl_choice[0], t_choice[0], pos)
            st.success("Added.")
            st.rerun()
        if st.button("Remove Track from Playlist"):
            remove_track_from_playlist(pl_choice[0], t_choice[0])
            st.success("Removed.")
            st.rerun()
    else:
        st.info("Add playlists and tracks first.")

# ------- JOIN: Tracks + Albums + Artists -------
elif menu == "JOIN: Tracks+Albums+Artists":
    st.header("JOIN: Tracks — Albums — Artists")
    rows = join_tracks_albums_artists()
    if rows:
        st.table([dict(r) for r in rows])
    else:
        st.info("No data available.")

