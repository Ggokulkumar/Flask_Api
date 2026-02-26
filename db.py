import json
import sqlite3
import logging
import config

logger = logging.getLogger(__name__)


def get_db():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    logger.info("Initializing database...")
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company_name TEXT,
            age INTEGER,
            city TEXT,
            state TEXT,
            zip TEXT,
            email TEXT,
            web TEXT
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]

    if count == 0:
        logger.info("Loading users from users.json...")
        with open('users.json', 'r') as f:
            users = json.load(f)
        for user in users:
            cursor.execute('''
                INSERT INTO users (first_name, last_name, company_name, age,
                                   city, state, zip, email, web)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['first_name'], user['last_name'], user['company_name'],
                user['age'], user['city'], user['state'], user['zip'],
                user['email'], user['web']
            ))
        conn.commit()
        logger.info(f"Loaded {len(users)} users into database.")
    else:
        logger.info(f"Database already has {count} users. Skipping JSON load.")

    conn.close()


def row_to_dict(row):
    return dict(row)
