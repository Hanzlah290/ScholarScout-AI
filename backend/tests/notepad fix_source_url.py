from sqlalchemy import text
from app.database.database import engine

url = "https://" + "english" + "." + "bit" + "." + "edu" + "." + "cn" + "/"

print("Python URL:", repr(url))

with engine.begin() as conn:
    conn.execute(
        text("UPDATE sources SET base_url = :url WHERE name = :name"),
        {
            "url": url,
            "name": "Beijing Institute of Technology",
        },
    )

print("Database URL updated.")
