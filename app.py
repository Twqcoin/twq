import os
import psycopg2

# الاتصال بقاعدة البيانات
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432))  # استخدام المنفذ الافتراضي 5432 إذا لم يتم تحديده
)

# إنشاء جدول (مثال)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS players (id SERIAL PRIMARY KEY, name TEXT, wallet TEXT)")
conn.commit()

# إغلاق الاتصال
cursor.close()
conn.close()
