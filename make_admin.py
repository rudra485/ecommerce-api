from app.db.database import sessionlocal
from app.models.user import User

db = sessionlocal()
user = db.query(User).filter(User.email == "test@test.com").first()
if user:
    user.is_admin = True
    db.commit()
    print(f"{user.email} is now an admin.")
else:
    print("User not found.")
db.close()