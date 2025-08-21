import pandas as pd
import numpy as np
import streamlit as st
import os 
import sys
from datetime import date, datetime, timedelta
from streamlit_echarts import st_echarts
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

class KpiServices:
    @staticmethod
    def analysis_user_stats(user_task_status: pd.DataFrame):
        """
        Analyze user task statistics.

        Args:
            user_task_status (pd.DataFrame): DataFrame with columns:
                ["Date", "completed_task", "total_task", "completion_percentage"]

        Returns:
            dict: {
                "total_dates": int,
                "sum_completed_tasks": int,
                "sum_total_tasks": int,
                "avg_completion_percentage": float,
                "active_days": int,
                "incomplete_tasks_list": int
            }
        """


        if user_task_status is None:
            return {
                "total_dates": 0,
                "sum_completed_tasks": 0,
                "sum_total_tasks": 0,
                "avg_completion_percentage": 0,
                "active_days": 0,
                "incomplete_tasks_list": 0
            }
        
        # Ensure correct columns
        required_cols = ["Date", "completed_task", "total_task", "completion_percentage"]
        if not all(col in user_task_status.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns {required_cols}")

        total_dates = user_task_status["Date"].nunique()
        sum_completed_tasks = int(user_task_status["completed_task"].sum())
        sum_total_tasks = int(user_task_status["total_task"].sum())
        avg_completion_percentage = round(float(user_task_status["completion_percentage"].mean()), 2)

        # Active days = days where total_task > 0
        active_days = int((user_task_status["total_task"] > 0).sum())

        # Incomplete tasks (overall)
        incomplete_tasks_list = int(user_task_status["total_task"].sum() - user_task_status["completed_task"].sum())

        return {
            "total_dates": total_dates,
            "sum_completed_tasks": sum_completed_tasks,
            "sum_total_tasks": sum_total_tasks,
            "avg_completion_percentage": avg_completion_percentage,
            "active_days": active_days,
            "incomplete_tasks_list": incomplete_tasks_list
        }

class GraphServices:
    @staticmethod
    def graph_analysis(user_task_status, filter_status,
                       bg_color="#fff",
                       title_color="#333",
                       indicator_color="#4c9f70"):
        if user_task_status is None:
            return GraphServices.make_graph([], [], "No Dates Available",
                                            bg_color, title_color, indicator_color)
        
        if "Current Month" in filter_status:
            return GraphServices.current_month(user_task_status,
                                               bg_color, title_color, indicator_color)
        elif "Last Month" in filter_status:
            return GraphServices.last_month(user_task_status,
                                            bg_color, title_color, indicator_color)
        elif "Month" in filter_status:
            return GraphServices.month(user_task_status,
                                       bg_color, title_color, indicator_color)
        elif "Year" in filter_status:
            return GraphServices.year(user_task_status,
                                      bg_color, title_color, indicator_color)
        elif "All Time" in filter_status:
            return GraphServices.all_time(user_task_status,
                                          bg_color, title_color, indicator_color)
        else:
            return GraphServices.make_graph([], [], "No Dates Available",
                                            bg_color, title_color, indicator_color)

    @staticmethod
    def current_month(df, bg_color, title_color, indicator_color):
        df["Date"] = pd.to_datetime(df["Date"])
        now = datetime.now()
        filtered = df[(df["Date"].dt.month == now.month) & (df["Date"].dt.year == now.year)]
        return GraphServices.make_graph(
            filtered["Date"].dt.strftime("%Y-%m-%d").tolist(),
            filtered["completion_percentage"].tolist(),
            "Completion % - Current Month",
            bg_color, title_color, indicator_color
        )

    @staticmethod
    def last_month(df, bg_color, title_color, indicator_color):
        df["Date"] = pd.to_datetime(df["Date"])
        if df.empty:
            return GraphServices.make_graph([], [], "No Dates Available",
                                            bg_color, title_color, indicator_color)
        last_date = df["Date"].max()
        prev_month = last_date.month - 1 if last_date.month > 1 else 12
        prev_year = last_date.year if last_date.month > 1 else last_date.year - 1
        filtered = df[(df["Date"].dt.month == prev_month) & (df["Date"].dt.year == prev_year)]
        return GraphServices.make_graph(
            filtered["Date"].dt.strftime("%Y-%m-%d").tolist(),
            filtered["completion_percentage"].tolist(),
            "Completion % - Last Month",
            bg_color, title_color, indicator_color
        )

    @staticmethod
    def month(df, bg_color, title_color, indicator_color):
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.strftime("%Y-%m")
        grouped = df.groupby("Month").apply(
            lambda x: (x["completed_task"].sum() / x["total_task"].sum()) * 100
            if x["total_task"].sum() > 0 else 0
        )
        return GraphServices.make_graph(
            grouped.index.tolist(),
            grouped.tolist(),
            "Completion % - Month Wise",
            bg_color, title_color, indicator_color
        )

    @staticmethod
    def year(df, bg_color, title_color, indicator_color):
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.year
        grouped = df.groupby("Year").apply(
            lambda x: (x["completed_task"].sum() / x["total_task"].sum()) * 100
            if x["total_task"].sum() > 0 else 0
        )
        return GraphServices.make_graph(
            grouped.index.astype(str).tolist(),
            grouped.tolist(),
            "Completion % - Year Wise",
            bg_color, title_color, indicator_color
        )

    @staticmethod
    def all_time(df, bg_color, title_color, indicator_color):
        df["Date"] = pd.to_datetime(df["Date"])
        return GraphServices.make_graph(
            df["Date"].dt.strftime("%Y-%m-%d").tolist(),
            df["completion_percentage"].tolist(),
            "Completion % - All Time",
            bg_color, title_color, indicator_color
        )

    @staticmethod
    def make_graph(x_data, y_data, title,
                   bg_color, title_color, indicator_color):
        if not x_data or not y_data:
            return {
                "title": {"text": "No Dates Available", "left": "center",
                          "textStyle": {"color": title_color}},
                "backgroundColor": bg_color,
                "series": []
            }

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": title_color}
            },
            "backgroundColor": bg_color,
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": x_data,
                "axisLine": {"lineStyle": {"color": title_color}}
            },
            "yAxis": {
                "type": "value",
                "name": "Completion %",
                "axisLine": {"lineStyle": {"color": title_color}},
                "splitLine": {"lineStyle": {"color": "#ddd"}}
            },
            "series": [
                {
                    "name": "Completion %",
                    "type": "line",
                    "areaStyle": {"color": indicator_color},
                    "lineStyle": {"color": indicator_color},
                    "itemStyle": {"color": indicator_color},
                    "smooth": True,
                    "data": y_data,
                }
            ]
        }
