from celery import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@localhost/db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.task(bind=True)
def db_task(self, operation):
    session = Session()
    try:
        session.execute(operation)  # Run SQL operation
        session.commit()  # Commit only if everything succeeds
    except Exception as e:
        session.rollback()  # Rollback in case of failure
        raise self.retry(exc=e, countdown=2)
    finally:
        session.close()
