"""SQLite-backed user accounts. Passwords are salted PBKDF2 hashes, never plaintext."""
import sqlite3, hashlib, hmac, os
from pathlib import Path
DB=str(Path(__file__).resolve().parents[1] / 'data' / 'supportpearlz_users.db')
def conn():
    os.makedirs('data',exist_ok=True)
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user',created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.commit(); return c
def _hash(password:str,salt:bytes|None=None):
    salt=salt or os.urandom(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,240000)
    return salt.hex()+':'+digest.hex()
def verify(password:str,stored:str):
    salt_hex,digest=stored.split(':')
    return hmac.compare_digest(_hash(password,bytes.fromhex(salt_hex)).split(':')[1],digest)
def ensure_admin(email:str,password:str):
    if not password: return
    c=conn(); row=c.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if not row:
        c.execute("INSERT OR IGNORE INTO users(email,password_hash,role) VALUES(?,?,'admin')",(email.lower(),_hash(password))); c.commit()
    c.close()
def register(email:str,password:str):
    if len(password)<10: raise ValueError('Password must contain at least 10 characters.')
    c=conn()
    try:
        c.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,'user')",(email.lower().strip(),_hash(password))); c.commit()
    except sqlite3.IntegrityError: raise ValueError('An account with this email already exists.')
    finally: c.close()
def login(email:str,password:str):
    c=conn(); row=c.execute('SELECT id,email,password_hash,role FROM users WHERE email=?',(email.lower().strip(),)).fetchone(); c.close()
    if row and verify(password,row[2]): return {'id':row[0],'email':row[1],'role':row[3]}
    return None
def users_summary():
    c=conn(); rows=c.execute('SELECT id,email,role,created_at FROM users ORDER BY id DESC').fetchall(); c.close(); return rows
