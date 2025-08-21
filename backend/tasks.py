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
            count_sql = "SELECT COUNT(*) as count FROM daily_plan"
            with connect.connection.cursor() as cursor:
                cursor.execute(count_sql)
                result = cursor.fetchone()
                
                if result:
                    plan_count = result['count']
                    plan_count += 1
                    pid = plan_count
                else:
                    pid = 1
                    
            return PlanServies.create_ids(pid)
            
        except Exception as e:
            print(f"Error generating plan ID: {e}")
            raise e
            
        finally:
            connect.disconnect()

    @staticmethod
    def add_plan(new_date):
        pass

class TaskSerives:

    @staticmethod
    def check_if_date_exist():
        pass

    @staticmethod
    def date_verification():
        pass

    @staticmethod
    def add_date():
        pass

    @staticmethod
    def add_date_in_databases():
        pass

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

