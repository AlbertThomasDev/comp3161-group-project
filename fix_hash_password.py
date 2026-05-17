from werkzeug.security import generate_password_hash
from app.database import get_db

db = get_db()
cursor = db.cursor()

hashed = generate_password_hash("password123")
cursor.execute("UPDATE users SET user_password = %s", (hashed,))
db.commit()

print(f"Updated {cursor.rowcount} users successfully.")
cursor.close()
db.close()