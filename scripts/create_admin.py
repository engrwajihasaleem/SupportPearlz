"""Create first admin account: ADMIN_EMAIL=... ADMIN_PASSWORD=... python scripts/create_admin.py"""
import os
from src.auth import ensure_admin,users_summary
email=os.environ.get('ADMIN_EMAIL','admin@pearlzhome.example'); password=os.environ.get('ADMIN_PASSWORD','')
if not password: raise SystemExit('Set ADMIN_PASSWORD in your shell before running this script.')
ensure_admin(email,password); print('Admin provisioning complete. Existing admin is not overwritten.')
