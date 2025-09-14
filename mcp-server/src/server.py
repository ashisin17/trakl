#!/usr/bin/env python3
import os
from fastmcp import FastMCP

from scheduler import scheduler, remind_user

from apscheduler.triggers.date import DateTrigger

mcp = FastMCP("Trackl MCP Server")

@mcp.tool(description="Schedule a task reminder for a user")
def schedule_task_reminder(email: str, subject: str, reminder_time_iso: str) -> str:
    from datetime import datetime
    reminder_datetime = datetime.fromisoformat(reminder_time_iso)
    scheduler.add_job(remind_user, trigger=DateTrigger(run_date=reminder_datetime), args=[email, subject])
    return f"Scheduled task reminder for {email} at {reminder_time_iso} about {subject}"


@mcp.tool(description="Greet a user by name with a welcome message from the MCP server")
def greet(name: str) -> str:
    return f"Hello, {name}! Welcome to our sample MCP server running on Heroku!"

@mcp.tool(description="Get information about the MCP server including name, version, environment, and Python version")
def get_server_info() -> dict:
    return {
        "server_name": "Sample MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting FastMCP server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
