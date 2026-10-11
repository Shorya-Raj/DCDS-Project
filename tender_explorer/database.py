"""Database connections and queries for structured tender data."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def mysql_connection():
    import mysql.connector

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "dcds"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "dcds_tenders"),
        connection_timeout=5,
    )


def mongo_collection():
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/"), serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    collection = client[os.getenv("MONGO_DATABASE", "dcds_tenders")]["tender_details"]
    return client, collection


def prepare_schema(connection):
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8-sig")
    statements = [statement.strip() for statement in schema.split(";") if statement.strip()]
    cursor = connection.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()


def upsert_tender(connection, record):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
            (record["category"],),
        )
        cursor.execute("SELECT category_id FROM categories WHERE name=%s", (record["category"],))
        category_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO locations (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
            (record["location"],),
        )
        cursor.execute("SELECT location_id FROM locations WHERE name=%s", (record["location"],))
        location_id = cursor.fetchone()[0]
        cursor.execute(
            """INSERT INTO tenders
               (tender_key, listing_id, title, category_id, location_id,
                estimated_value_inr, emd_inr, closing_date, source_url)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
               title=VALUES(title), category_id=VALUES(category_id),
               location_id=VALUES(location_id),
               estimated_value_inr=VALUES(estimated_value_inr),
               emd_inr=VALUES(emd_inr), closing_date=VALUES(closing_date),
               source_url=VALUES(source_url)""",
            (
                record["tender_key"], record["listing_id"], record["title"],
                category_id, location_id, record["estimated_value_inr"],
                record["emd_inr"], record["closing_date"], record["source_url"],
            ),
        )
    finally:
        cursor.close()


def read_tenders(connection):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT t.tender_key, t.listing_id, t.title, c.name AS category,
                      l.name AS location, t.estimated_value_inr, t.emd_inr,
                      t.closing_date, t.source_url
               FROM tenders AS t
               JOIN categories AS c ON c.category_id=t.category_id
               JOIN locations AS l ON l.location_id=t.location_id
               ORDER BY t.closing_date, t.tender_key"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
