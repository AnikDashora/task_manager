import pandas as pd
import numpy as np
import streamlit as st
import os 
import sys
from datetime import date, datetime, timedelta
from streamlit_echarts import st_echarts
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.database import SqlConnection
from models.task_model import UserTasks

class PlanServies:
    @staticmethod
    def create_ids(pid):
        if(isinstance(pid,str)):
            raise ValueError
        id_len = 4
        if(len(str(pid)) <= 4):
            prefix_len = id_len - len(str(pid))
            return "p"+"0"*prefix_len+str(pid)
        else:
            return "p"+str(pid)
    
    @staticmethod
    def generate_plan_id():
        """
        Generate a new user ID by checking the database for existing users
        
        Returns:
            int: Next available user ID
            
        Raises:
            Exception: If database connection fails or other database errors occur
        """
        connect = SqlConnection()
        
        try:
            if not connect.connect():
                raise Exception("Failed to connect to database")
            
            # Check if users table exists
            table_check_sql = "SHOW TABLES LIKE 'daily_plan'"
            with connect.connection.cursor() as cursor:
                cursor.execute(table_check_sql)
                table_exists = cursor.fetchone()
                
                if not table_exists:
                    raise Exception("daily_plan table does not exist in database")
            
            # Get the count of existing users
            count_sql = "SELECT MAX(CAST(SUBSTRING(plan_id, 2) AS UNSIGNED)) AS max_id FROM daily_plan"
            with connect.connection.cursor() as cursor:
                cursor.execute(count_sql)
                result = cursor.fetchone()
                
                if result and result['max_id'] is not None:
                    pid = result['max_id'] + 1
                else:
                    pid = 1
            return PlanServies.create_ids(pid)
            
        except Exception as e:
            print(f"Error generating plan ID: {e}")
            raise e
            
        finally:
            connect.disconnect()

    @staticmethod
    def add_plan(new_date,user_id):
        """
        Add a new daily plan for a given user on a specific date.

        Args:
            new_date (str): Date of the plan in "YYYY-MM-DD" format.
            user_id (str): Unique ID of the user.

        Returns:
            str: The newly generated plan_id if insertion is successful.

        Raises:
            ValueError: If new_date or user_id is invalid.
            Exception: If database errors occur (e.g., duplicate plan, connection issues).
        """
        # ✅ Validate inputs
        if not new_date or not isinstance(new_date, str):
            raise ValueError("Invalid date format: must be a non-empty string in 'YYYY-MM-DD' format")
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id: must be a non-empty string")

        # ✅ Validate date format
        try:
            plan_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format: must be 'YYYY-MM-DD'")

        # ✅ Connect to database
        connect = SqlConnection()
        try:
            if not connect.connect():
                raise Exception("Failed to connect to database")

            with connect.connection.cursor() as cursor:
                # 🔍 Check if a plan already exists for this user on this date
                check_sql = """
                    SELECT plan_id 
                    FROM daily_plan 
                    WHERE user_id = %s AND plan_date = %s
                """
                cursor.execute(check_sql, (user_id, plan_date))
                existing = cursor.fetchone()
                if existing:
                    raise Exception(f"Plan already exists for user {user_id} on {new_date}")

                # 🔑 Generate new plan_id
                new_plan_id = PlanServies.generate_plan_id()

                # 📝 Insert into daily_plan
                insert_sql = """
                    INSERT INTO daily_plan (plan_id, user_id, plan_date, total_task, completed_task)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (new_plan_id, user_id, plan_date, 0, 0))

                # 💾 Commit the transaction
                connect.connection.commit()

                return new_plan_id

        except Exception as e:
            # ❌ Rollback on error
            if connect.connection:
                connect.connection.rollback()
            print(f"Error adding plan: {e}")
            raise e

        finally:
            connect.disconnect()

    @staticmethod
    def delete_plan(plan_id):
        """
        Delete a daily plan and its associated tasks.
        (tasks will be auto-deleted because of ON DELETE CASCADE)

        Args:
            plan_id (str): Unique plan ID to delete.

        Returns:
            bool: True if deletion successful, False otherwise.
        """
        if not plan_id or not isinstance(plan_id, str):
            raise ValueError("Invalid plan_id: must be a non-empty string")

        connect = SqlConnection()
        try:
            if not connect.connect():
                raise Exception("Failed to connect to database")

            with connect.connection.cursor() as cursor:
                delete_plan_sql = "DELETE FROM daily_plan WHERE plan_id = %s"
                cursor.execute(delete_plan_sql, (plan_id,))
                connect.connection.commit()
                return True

        except Exception as e:
            if connect.connection:
                connect.connection.rollback()
            print(f"Error deleting plan: {e}")
            raise e

        finally:
            connect.disconnect()

class TaskSerives:

    @staticmethod
    def check_if_date_exist(user_tasks, new_date: str) -> bool:
        """
        Check if the given date already exists in the user's tasks.

        Args:
            user_tasks (UserTasks): An instance of UserTasks class.
            new_date (str): Date string in "YYYY-MM-DD" format.

        Returns:
            bool: True if the date exists, False otherwise.

        Raises:
            ValueError: If inputs are invalid.
        """ 

        # Validate input types
        if not isinstance(user_tasks, UserTasks):
            raise ValueError("user_tasks must be an instance of UserTasks class")
        if not isinstance(new_date, str) or not new_date.strip():
            raise ValueError("new_date must be a non-empty string")

        # Check if any tasks exist for that date
        if user_tasks.user_tasks and new_date in user_tasks.user_tasks:
            return True
        return False

    @staticmethod
    def date_verification(new_date: str) -> date:
        """
        Verify that the given date is valid, in correct format (YYYY-MM-DD),
        and not before today's date.

        Args:
            new_date (str): Date string in "YYYY-MM-DD" format.

        Returns:
            datetime.date: Parsed date object.

        Raises:
            ValueError: If new_date is not in the correct format or is before today.
        """
        if not isinstance(new_date, str) or not new_date.strip():
            raise ValueError("new_date must be a non-empty string")

        try:
            parsed_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format, must be 'YYYY-MM-DD'")

        # ✅ Check if date is before today
        if parsed_date < date.today():
            st.warning("Can add pervious dates")
            return None

        return parsed_date

    @staticmethod
    def add_date(user_id: str, user_tasks_obj, new_date: str) -> str:
        """
        Add a new date (plan) for the given user if it passes all validations.

        Steps:
        1. Validate that the date is today or in the future (via date_verification).
        2. Ensure that the date does not already exist in the user's tasks.
        3. Insert the new plan into the database.
        4. Update:
            - plan_status DataFrame
            - plan_ids dictionary
            - user_tasks.user_tasks dictionary
            - user_tasks.show_user_task dictionary (sorted order)

        Args:
            user_id (str): User ID (e.g., "u0001").
            user_tasks (UserTasks): Instance of UserTasks class.
            new_date (str): Date string in "YYYY-MM-DD" format.

        Returns:
            str: The newly generated plan_id if insertion is successful.

        Raises:
            ValueError: If inputs are invalid or validations fail.
            Exception: If database errors occur.
        """
        # ✅ Step 1: Verify date
        parsed_date = TaskSerives.date_verification(new_date)
        if(parsed_date is None):
            return None
        # ✅ Step 2: Check if date already exists
        if TaskSerives.check_if_date_exist(user_tasks_obj, new_date):
            st.warning("Date already exist in calander")
            return None

        # ✅ Step 3: Add plan into DB
        new_plan_id = PlanServies.add_plan(new_date, user_id)

        # ✅ Step 4: Update in-memory objects

        # --- 4.1 Update plan_ids ---
        user_tasks_obj.plan_ids[new_plan_id] = new_date

        # --- 4.2 Update plan_status DataFrame ---
        new_row = {
            "Date": new_date,
            "completed_task": 0,
            "total_task": 0,
            "completion_percentage": 0.0,
        }
        user_tasks_obj.plan_status = pd.concat(
            [user_tasks_obj.plan_status, pd.DataFrame([new_row])],
            ignore_index=True
        )

        # --- 4.3 Update user_tasks dict ---
        user_tasks_obj.user_tasks[new_date] = {}   # empty task list for that date

        # --- 4.4 Update show_user_task dict (maintain sorting) ---
        user_tasks_obj.show_user_task[new_date] = {}

        today = date.today()

        def custom_sort(d):
            d = datetime.strptime(d, "%Y-%m-%d").date()
            if d == today:
                return (0, 0)  # today first
            elif d > today:
                return (1, (d - today).days)  # future ascending
            else:
                return (2, -(d - today).days)  # past descending

        sorted_items = sorted(user_tasks_obj.show_user_task.items(), key=lambda x: custom_sort(x[0]))
        user_tasks_obj.show_user_task = dict(sorted_items)

        return new_plan_id

    @staticmethod
    def delete_date(user_id, user_tasks_obj, date):
        """
        Delete a given date (plan) for a user from:
        - user_tasks_obj.plan_ids
        - user_tasks_obj.plan_status
        - user_tasks_obj.user_tasks
        - user_tasks_obj.show_user_task
        And also remove it from the database (daily_plan + tasks).
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id")
        if not isinstance(user_tasks_obj, UserTasks):
            raise ValueError("user_tasks_obj must be an instance of UserTasks")
        if not date or not isinstance(date, str):
            raise ValueError("Invalid date format, expected 'YYYY-MM-DD'")

        # 1. Find plan_id for the given date
        plan_id_to_delete = None
        for pid, d in user_tasks_obj.plan_ids.items():
            if str(d) == date:
                plan_id_to_delete = pid
                break

        if not plan_id_to_delete:
            raise ValueError(f"No plan found for date {date} and user {user_id}")

        # 2. Delete from database
        try:
            PlanServies.delete_plan(plan_id_to_delete)
        except Exception as e:
            print(f"Database deletion failed: {e}")
            raise e

        # 3. Remove from in-memory structures
        # (a) plan_ids
        if plan_id_to_delete in user_tasks_obj.plan_ids:
            del user_tasks_obj.plan_ids[plan_id_to_delete]

        # (b) plan_status (filter out the row with this date)
        if not user_tasks_obj.plan_status.empty:
            user_tasks_obj.plan_status = user_tasks_obj.plan_status[
                user_tasks_obj.plan_status["Date"] != date
            ].reset_index(drop=True)

        # (c) user_tasks
        if date in user_tasks_obj.user_tasks:
            del user_tasks_obj.user_tasks[date]

        # (d) show_user_task
        if date in user_tasks_obj.show_user_task:
            del user_tasks_obj.show_user_task[date]

        return True

    @staticmethod
    def get_date_detail(date_str: str) -> str:
        """
        Convert a date string into 'Today', 'Tomorrow', 'Yesterday',
        or a formatted full date.
        """
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()

        if input_date == today:
            return "Today"
        elif input_date == today + timedelta(days=1):
            return "Tomorrow"
        elif input_date == today - timedelta(days=1):
            return "Yesterday"
        else:
            return input_date.strftime("%a %b-%d, %Y")
    
    @staticmethod
    def get_badge_status(current_date_task: dict) -> str:
        """
        Determine badge status for a given day's tasks.

        Args:
            current_date_task (dict): Dictionary of tasks {"Task 1": "Complete", "Task 2": "Incomplete"}

        Returns:
            str: Badge status -> "badge-complete", "badge-medium", "badge-no-tasks"
        """
        if not current_date_task:  # no tasks
            return "badge-no-tasks"

        statuses = list(current_date_task.values())

        if all(s == "Completed" for s in statuses):
            return "badge-complete"
        elif any(s == "Incomplete" for s in statuses):
            return "badge-medium"
        else:
            return "badge-no-tasks"
        
    @staticmethod
    def get_task_status(current_date_task: dict) -> str:
        """
        Return task status for a given day's tasks.

        Args:
            current_date_task (dict): {"Task 1": "Complete", "Task 2": "Incomplete"}

        Returns:
            str: "No Task" if no tasks,
                otherwise "X/Y" where X = completed tasks, Y = total tasks
        """
        if not current_date_task:  # no tasks
            return "No Task"

        total_tasks = len(current_date_task)
        completed_tasks = sum(1 for status in current_date_task.values() if status == "Completed")

        return f"{completed_tasks}/{total_tasks}"
    
    @staticmethod
    def get_progress_percent(current_date_task: dict) -> int:
        """
        Calculate the progress percentage of tasks for a given date.

        Args:
            current_date_task (dict): A dictionary in the format {"Task": "Status"} where:
                - Task (str): The name of the task.
                - Status (str): Either "Complete" or "Incomplete".

        Returns:
            int: The completion percentage (0 - 100).
                - Returns 0 if there are no tasks.
                - Returns 0 if no tasks are marked as "Complete".
                - Otherwise, calculates (completed_tasks / total_tasks) * 100.
        """

        if not current_date_task:
            return 0

        total_tasks = len(current_date_task)

        completed_tasks = sum(1 for status in current_date_task.values() if status == "Complete")

        if completed_tasks == 0 or total_tasks == 0:
            return 0

        return int((completed_tasks / total_tasks) * 100)
    
    @staticmethod
    def get_task_exist(current_date_tasks: dict) -> bool:
        """
        Check if tasks exist for the given date.

        Args:
            current_date_tasks (dict): {"Task 1": "Complete", "Task 2": "Incomplete"}

        Returns:
            bool: True if there is at least one task, False otherwise
        """
        return bool(current_date_tasks)

    @staticmethod
    def get_progress_percent(current_date_task: dict) -> int:
        """
        Calculate the progress percentage of tasks for a given date.

        Args:
            current_date_task (dict): A dictionary in the format {"Task": "Status"} where:
                - Task (str): The name of the task.
                - Status (str): Either "Complete" or "Incomplete".

        Returns:
            int: The completion percentage (0–100).
                - Returns 0 if there are no tasks.
                - Returns 0 if no tasks are marked as "Complete".
                - Otherwise, calculates (completed_tasks / total_tasks) * 100.
        """

        # Check if there are no tasks in the given date
        if not current_date_task:
            return 0

        # Total number of tasks (dict keys)
        total_tasks = len(current_date_task)

        # Count how many tasks are completed (status == "Complete")
        completed_tasks = sum(1 for status in current_date_task.values() if status == "Completed")

        # If no tasks are completed or total is 0, return 0
        if completed_tasks == 0 or total_tasks == 0:
            return 0

        # Calculate and return the completion percentage as an integer
        return int((completed_tasks / total_tasks) * 100)
    
    @staticmethod
    def if_task_completed(current_task: str, current_date_task: dict) -> bool:
        """
        Check if a specific task is completed.

        Args:
            current_task (str): Task name (key in the dict)
            current_date_task (dict): {"Task 1": "Complete", "Task 2": "Incomplete"}

        Returns:
            bool: True if the task exists and is marked 'Complete', else False
        """
        return current_date_task.get(current_task) == "Completed"

