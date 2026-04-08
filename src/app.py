"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlmodel import Session, select

from database import create_db_and_tables, get_session, engine
from models import Activity, Student, Enrollment

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Default seed data for initial activities
DEFAULT_ACTIVITIES = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
]


def seed_database():
    """Seed the database with default activities and participants"""
    session = Session(engine)
    try:
        # Check if database is already seeded
        statement = select(Activity)
        existing = session.exec(statement).first()
        if existing is not None:
            return
        
        # Seed activities
        for activity_data in DEFAULT_ACTIVITIES:
            activity = Activity(
                name=activity_data["name"],
                description=activity_data["description"],
                schedule=activity_data["schedule"],
                max_participants=activity_data["max_participants"]
            )
            session.add(activity)
            session.flush()
            
            # Add participants
            for email in activity_data["participants"]:
                # Create or get student
                statement = select(Student).where(Student.email == email)
                student = session.exec(statement).first()
                if not student:
                    student = Student(email=email)
                    session.add(student)
                    session.flush()
                
                # Create enrollment
                enrollment = Enrollment(
                    student_id=student.id,
                    activity_id=activity.id
                )
                session.add(enrollment)
        
        session.commit()
    finally:
        session.close()


@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    create_db_and_tables()
    seed_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)):
    """Get all activities with their current participants"""
    statement = select(Activity)
    activities_list = session.exec(statement).all()
    
    # Convert to dictionary format for backward compatibility with frontend
    result = {}
    for activity in activities_list:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [enrollment.student.email for enrollment in activity.enrollments]
        }
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    """Sign up a student for an activity"""
    # Get activity by name
    statement = select(Activity).where(Activity.name == activity_name)
    activity = session.exec(statement).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if student is already enrolled
    statement = select(Enrollment).where(
        (Enrollment.activity_id == activity.id) &
        (Enrollment.student_id == select(Student.id).where(Student.email == email))
    )
    
    # Get or create student
    statement = select(Student).where(Student.email == email)
    student = session.exec(statement).first()
    if not student:
        student = Student(email=email)
        session.add(student)
        session.flush()
    
    # Check for existing enrollment
    statement = select(Enrollment).where(
        (Enrollment.activity_id == activity.id) &
        (Enrollment.student_id == student.id)
    )
    existing_enrollment = session.exec(statement).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check if activity is at capacity
    if activity.participant_count >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at maximum capacity"
        )
    
    # Create enrollment
    enrollment = Enrollment(student_id=student.id, activity_id=activity.id)
    session.add(enrollment)
    session.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    """Unregister a student from an activity"""
    # Get activity by name
    statement = select(Activity).where(Activity.name == activity_name)
    activity = session.exec(statement).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get student
    statement = select(Student).where(Student.email == email)
    student = session.exec(statement).first()
    
    if not student:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Get enrollment
    statement = select(Enrollment).where(
        (Enrollment.activity_id == activity.id) &
        (Enrollment.student_id == student.id)
    )
    enrollment = session.exec(statement).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove enrollment
    session.delete(enrollment)
    session.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
