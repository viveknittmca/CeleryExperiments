from celery import Celery, chord
import random
import time

from tasks import task_function, final_callback, process_file, write_to_db

# Creating a chord: A group of tasks followed by a callback
# What Happens Here?
# Task 1, Task 2, and Task 3 execute in parallel.
# Each task retries up to 3 times if it fails.
# If all succeed, final_callback executes and writes results.
# If any task fails even after retries, the final callback is skipped.
task_chord = chord([
    task_function.s("Task 1"),
    task_function.s("Task 2"),
    task_function.s("Task 3")
])(final_callback.s())  # Callback is executed only if all tasks succeed

print("Chord dispatched!")


# Scenario: Processing Files in Parallel and Writing Only on Success
# Imagine you have a system where:
#
# You process multiple files concurrently.
# If all files are processed successfully, the system writes to a database.

# Using Chord
chord([
    process_file.s("file1.csv"),
    process_file.s("file2.csv"),
    process_file.s("file3.csv")
])(write_to_db.s())

print("File processing workflow dispatched!")


