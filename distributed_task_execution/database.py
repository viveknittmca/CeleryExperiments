# Using Database Transactions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def execute_tasks_with_db_transaction():
    session = Session()
    try:
        session.execute("INSERT INTO results (task_name, status) VALUES ('Task 1', 'Completed')")
        session.execute("INSERT INTO results (task_name, status) VALUES ('Task 2', 'Completed')")
        session.execute("INSERT INTO results (task_name, status) VALUES ('Task 3', 'Completed')")

        session.commit()  # Only commits if everything succeeds
        print("All tasks succeeded. Results committed.")
    except Exception as e:
        session.rollback()  # Rollback if any failure occurs
        print("Execution failed. No state is leaked:", str(e))
    finally:
        session.close()
