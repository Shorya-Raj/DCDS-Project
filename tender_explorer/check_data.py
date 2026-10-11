"""Check SQL and MongoDB tender ID consistency."""
from tender_explorer.database import mysql_connection, mongo_collection


def main():
    sql = mysql_connection()
    mongo_client, details = mongo_collection()
    try:
        cursor = sql.cursor()
        cursor.execute("SELECT tender_key FROM tenders")
        sql_ids = {row[0] for row in cursor.fetchall()}
        mongo_ids = {row["_id"] for row in details.find({}, {"_id": 1})}
        cursor.close()
        print(f"MySQL: {len(sql_ids)} IDs; MongoDB: {len(mongo_ids)} IDs")
        only_sql = sorted(sql_ids - mongo_ids)
        only_mongo = sorted(mongo_ids - sql_ids)
        if only_sql or only_mongo:
            print(f"Only in MySQL: {only_sql[:10]}")
            print(f"Only in MongoDB: {only_mongo[:10]}")
            raise SystemExit(1)
        print("The two databases contain matching tender IDs.")
    finally:
        mongo_client.close()
        sql.close()


if __name__ == "__main__":
    main()
