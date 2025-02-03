from celery import Celery, chain
from celery.exceptions import Retry
import random
import time

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task(bind=True, max_retries=3)
def validate_user_data(self, user_id):
    """Validate user data"""
    print(f"Validating user {user_id}...")
    if random.random() < 0.2:
        raise self.retry(exc=Exception("Validation failed"), countdown=2)
    return f"User {user_id} validated"


@app.task(bind=True, max_retries=3)
def send_verification_email(self, user_id):
    """Send verification email"""
    print(f"Sending verification email to {user_id}...")
    if random.random() < 0.2:
        raise self.retry(exc=Exception("Email sending failed"), countdown=2)
    return f"Verification email sent to {user_id}"


@app.task(bind=True, max_retries=3)
def generate_auth_token(self, user_id):
    """Generate authentication token"""
    print(f"Generating auth token for {user_id}...")
    if random.random() < 0.2:
        raise self.retry(exc=Exception("Token generation failed"), countdown=2)
    return f"Auth token generated for {user_id}"


@app.task(ignore_result=True)
def log_signup_attempt(user_id):
    """Log the signup attempt (optional)"""
    print(f"Logging signup attempt for {user_id}...")
    if random.random() < 0.3:
        print(f"Logging failed for {user_id}, but proceeding...")
    return "Logged"


@app.task
def write_to_database(user_id):
    """Write user to database only if all required steps succeed"""
    print(f"Writing user {user_id} to the database...")
    return f"User {user_id} successfully registered!"


workflow = chain(
    validate_user_data.s("User123"),
    send_verification_email.s(),
    generate_auth_token.s(),
    log_signup_attempt.s(),  # This step can fail without stopping the chain
    write_to_database.s()
)

workflow.apply_async()
print("Signup workflow dispatched!")


# Dynamically Triggering Tasks Based on Message Content
@app.task
def process_event(message):
    event_type = message.get("event_type")

    if event_type == "user_signup":
        workflow2 = chain(
            validate_user_data.s(message["user_id"]),
            send_verification_email.s(),
            generate_auth_token.s(),
            log_signup_attempt.s(),
            write_to_database.s()
        )
    # elif event_type == "user_delete":
        # workflow2 = chain(delete_user_data.s(message["user_id"]))

    workflow2.apply_async()


# Dynamically Setting ignore_result=True at Runtime
# Since ignore_result=True is defined at compile time, you can control it dynamically using task options at runtime.
# Solution: Pass ignore_result at Runtime

@app.task(bind=True)
def log_signup_attempt(self, user_id, ignore_result=False):
    """Log the signup attempt"""
    print(f"Logging signup attempt for {user_id}...")
    if random.random() < 0.3:
        print(f"Logging failed for {user_id}, but proceeding...")

    if ignore_result:
        return None  # Simulate ignored result at runtime
    return "Logged"
