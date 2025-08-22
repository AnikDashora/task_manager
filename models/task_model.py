import os
import sys
import pandas as pd
from datetime import datetime, date
import streamlit as st

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.database import SqlConnection


class PlanDate:
    def __init__(self):
        # always start with empty structures (avoid NoneType issues)
        self.plan_ids = {}   # {plan_id: "YYYY-MM-DD"}
        self.plan_status = pd.DataFrame(
            columns=["Date", "completed_task", "total_task", "completion_percentage"]
        )

    def set_user_plan(self, user_id):
        """
        Fetches all plan_ids and plan status for a given user_id
        from the daily_plan table and stores it in a pandas DataFrame.
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id provided")

        db = SqlConnection()
        try:
            if not db.connect():
                raise ConnectionError("Failed to connect to the database")

            with db.connection.cursor() as cursor:
                query = """
                    SELECT plan_id, plan_date, total_task, completed_task
                    FROM daily_plan
                    WHERE user_id = %s
                    ORDER BY plan_date ASC
                """
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()

                if not results:
                    self.plan_ids = {}
                    self.plan_status = pd.DataFrame(
                        columns=["Date", "completed_task", "total_task", "completion_percentage"]
                    )
                    return

                # Map plan_ids
                self.plan_ids = {row["plan_id"]: str(row["plan_date"]) for row in results}

                # Create DataFrame
                df = pd.DataFrame(results)
                df = df.rename(columns={"plan_date": "Date"})

                # Calculate completion percentage safely
                df["completion_percentage"] = (
                    (df["completed_task"] / df["total_task"] * 100)
                    .fillna(0)
                    .replace([float("inf"), -float("inf")], 0)
                    .round(2)
                )

                self.plan_status = df[["Date", "completed_task", "total_task", "completion_percentage"]]

        except Exception as e:
            print(f"Error fetching user plans: {e}")
            self.plan_ids = {}
            self.plan_status = pd.DataFrame(
                columns=["Date", "completed_task", "total_task", "completion_percentage"]
            )
        finally:
            db.disconnect()


class UserTasks(PlanDate):
    def __init__(self):
        super().__init__()   # initialize plan_ids and plan_status
        self.user_tasks = {}       # { "YYYY-MM-DD": {task: status, ...} }
        self.show_user_task = {}   # sorted view

    def set_user_tasks(self, user_id):
        """
        Fetch all tasks for a given user_id across all plans
        using a single SQL query with IN operation.
        Builds dict: { "date": {"Task1": status, "Task2": status, ...}, ... }
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id provided")

        # fetch plans
        self.set_user_plan(user_id)

        if not self.plan_ids:
            self.user_tasks = {}
            return

        db = SqlConnection()
        try:
            if not db.connect():
                raise ConnectionError("Failed to connect to the database")

            with db.connection.cursor() as cursor:
                plan_ids = list(self.plan_ids.keys())
                placeholders = ", ".join(["%s"] * len(plan_ids))

                query = f"""
                    SELECT t.plan_id, dp.plan_date, t.title, t.status
                    FROM tasks t
                    JOIN daily_plan dp ON t.plan_id = dp.plan_id
                    WHERE t.plan_id IN ({placeholders})
                    ORDER BY dp.plan_date ASC, t.created_at ASC
                """
                cursor.execute(query, tuple(plan_ids))
                results = cursor.fetchall()

                tasks_dict = {}

                if not results:
                    # No tasks found → fallback to empty dicts for all plan dates
                    tasks_dict = {str(date): {} for date in self.plan_ids.values()}
                else:
                    for row in results:
                        plan_date = str(row["plan_date"])
                        task_title = row["title"]
                        task_status = row["status"]

                        if plan_date not in tasks_dict:
                            tasks_dict[plan_date] = {}

                        tasks_dict[plan_date][task_title] = task_status

                    # Ensure all plan dates are represented (even if no tasks on some days)
                    for plan_date in self.plan_ids.values():
                        plan_date = str(plan_date)
                        if plan_date not in tasks_dict:
                            tasks_dict[plan_date] = {}

                self.user_tasks = tasks_dict

        except Exception as e:
            print(f"Error fetching user tasks: {e}")
            # fallback → empty dicts for all plan dates
            self.user_tasks = {str(date): {} for date in self.plan_ids.values()}
        finally:
            db.disconnect()

    def set_show_user_tasks(self, user_id):
        """
        Filters user tasks to current month.
        If no tasks in current month, fallback to the latest available month.
        Then applies custom sorting order:
        Today → Future dates (ascending) → Past dates (descending).
        """
        if not self.user_tasks:
            self.set_user_tasks(user_id)

        if not self.user_tasks:
            self.show_user_task = {}
            return

        df = pd.DataFrame([
            {"Date": datetime.strptime(date, "%Y-%m-%d").date(), "Tasks": tasks}
            for date, tasks in self.user_tasks.items()
        ])

        if df.empty:
            self.show_user_task = {}
            return

        now = datetime.now()
        current_year, current_month = now.year, now.month

        # Filter for current month
        current_month_df = df[
            (df["Date"].apply(lambda d: d.year) == current_year) &
            (df["Date"].apply(lambda d: d.month) == current_month)
        ]

        # If no tasks in current month, fallback to latest available month
        if current_month_df.empty:
            df["YearMonth"] = df["Date"].apply(lambda d: d.replace(day=1))
            latest_month = df["YearMonth"].max()
            df = df[df["YearMonth"] == latest_month]
        else:
            df = current_month_df

        if df.empty:
            self.show_user_task = {}
            return

        # Custom sorting
        today = date.today()
        def custom_sort(d):
            if d == today:
                return (0, 0)
            elif d > today:
                return (1, (d - today).days)
            else:
                return (2, -(d - today).days)

        df["sort_key"] = df["Date"].apply(custom_sort)
        df = df.sort_values("sort_key").drop(columns="sort_key").reset_index(drop=True)

        # Back to dict
        self.show_user_task = {
            d.strftime("%Y-%m-%d"): t for d, t in zip(df["Date"], df["Tasks"])
        }
