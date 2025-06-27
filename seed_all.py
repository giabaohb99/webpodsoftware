import logging
from faker import Faker
from sqlalchemy.orm import Session

# --- Setup Paths and Logging ---
import sys
import os
sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Import all necessary components ---
from core.core.database import SessionLocal, Base, engine
# Import all models to ensure they are registered with Base
from users.models import User
from employee.models import Employee
from role.models import Role, UserRole
from story.models import Story
# Import schemas and CRUD functions
from core.core.security import get_password_hash
from role.schemas import DEFAULT_ROLES
from story.schemas import StoryCreate
from story.crud import create_story as create_story_crud

# --- Seeding Functions ---

def seed_users_and_employees(db: Session, num_users: int = 20):
    logger.info("--- Seeding Users and Employees ---")
    if db.query(User).first():
        logger.info("Users already seeded. Skipping.")
        return
    
    fake = Faker()
    default_hashed_password = get_password_hash("password123")
    for i in range(num_users):
        user = User(
            username=f"testuser{i}" if i > 0 else "testuser",
            hashed_password=default_hashed_password,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        employee = Employee(
            user_id=user.id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            status=1
        )
        db.add(employee)
    db.commit()
    logger.info(f"Successfully seeded {num_users} users and employees.")

def seed_roles(db: Session):
    logger.info("--- Seeding Roles ---")
    if db.query(Role).first():
        logger.info("Roles already seeded. Skipping.")
        return

    for role_data in DEFAULT_ROLES:
        db.add(Role(**role_data))
    db.commit()
    
    # Assign roles to testuser
    user = db.query(User).filter_by(username="testuser").first()
    admin_role = db.query(Role).filter_by(name="admin").first()
    story_role = db.query(Role).filter_by(name="story_manager").first()
    
    if user and admin_role:
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
    if user and story_role:
        db.add(UserRole(user_id=user.id, role_id=story_role.id))
        
    db.commit()
    logger.info("Successfully seeded roles and assigned to 'testuser'.")

def seed_stories(db: Session, num_stories: int = 5):
    logger.info("--- Seeding Stories ---")
    if db.query(Story).first():
        logger.info("Stories already seeded. Skipping.")
        return
        
    author = db.query(User).filter_by(username="testuser").first()
    if not author:
        logger.warning("Could not find 'testuser' to seed stories.")
        return

    fake = Faker('vi_VN') # Use Vietnamese Faker
    for _ in range(num_stories):
        story_data = StoryCreate(
            title=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=2),
            content=fake.paragraph(nb_sentences=10),
            tags="sample, seed, data",
            published=True
        )
        create_story_crud(db, story_data, author_id=author.id)
    db.commit()
    logger.info(f"Successfully seeded {num_stories} stories.")

# --- Main Execution ---

if __name__ == "__main__":
    logger.info("Starting master seeding process...")
    db = SessionLocal()
    
    try:
        # Step 1: Create all tables
        logger.info("Creating all tables from Base metadata...")
        Base.metadata.create_all(bind=engine)
        
        # Step 2: Seed data in order
        seed_users_and_employees(db)
        seed_roles(db)
        seed_stories(db)
        
        logger.info("="*50)
        logger.info("Master seeding process completed successfully!")
        logger.info("Login with username: 'testuser', password: 'password123'")
        logger.info("="*50)

    except Exception as e:
        logger.error(f"An error occurred during the seeding process: {e}")
        db.rollback()
    finally:
        db.close() 