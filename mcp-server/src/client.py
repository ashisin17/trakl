# client.py
import asyncio
from fastmcp import Client
from datetime import datetime, timedelta

run_date = datetime.now() + timedelta(seconds=2)

async def main():
    from server import mcp  # assuming server.py defines `mcp = FastMCP(...)`
    async with Client(mcp) as client2:
        print("Connected in-memory!")

        res3 = await client2.call_tool("schedule_task_reminder", {
          "email": "nj421@ic.ac.uk",
          "subject": "Study Chemistry",
          "reminder_time_iso": run_date.isoformat()
        })
        print("Schedule Task Reminder →", res3.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
