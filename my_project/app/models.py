import psycopg2
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )

def create_table():
    """إنشاء جدول players إذا لم يكن موجودًا."""
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        image_url TEXT NOT NULL
                    );
                """)
                print("تم إنشاء الجدول بنجاح!")
    except Exception as e:
        print(f"حدث خطأ: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def insert_player(name, image_url):
    """إدراج لاعب جديد في الجدول."""
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO players (name, image_url)
                    VALUES (%s, %s) RETURNING id;
                """, (name, image_url))
                player_id = cursor.fetchone()[0]
                print(f"تم إضافة اللاعب {name} بنجاح! (ID: {player_id})")
                return player_id
    except Exception as e:
        print(f"حدث خطأ: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_players():
    """استرجاع جميع اللاعبين من الجدول."""
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, image_url FROM players;")
                players = cursor.fetchall()
                return players
    except Exception as e:
        print(f"حدث خطأ: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
