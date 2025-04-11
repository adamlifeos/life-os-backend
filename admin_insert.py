from app.database import SessionLocal

# Adjust the User import if needed (e.g. from app.models import User)
from app.models import User

from passlib.context import CryptContext

# Ensure the hashing configuration matches your backend's current configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def insert_admin_user():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == 'adam827@gmail.com').first()
        if existing_user:
            print('Admin user already exists.')
            return
        
        hashed_password = get_password_hash('password123')
        admin_user = User(email='adam827@gmail.com', hashed_password=hashed_password)
        db.add(admin_user)
        db.commit()
        print('Admin user created successfully.')
    except Exception as e:
        db.rollback()
        print(f'Error inserting admin user: {e}')
    finally:
        db.close()


if __name__ == '__main__':
    insert_admin_user()
