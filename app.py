from flask import Flask, request, jsonify
import psycopg2
import redis

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="YOUR_DB_NAME",
    user="YOUR_DB_USER",
    password="YOUR_DB_PASSWORD",
    host="YOUR_DB_HOST",
    port="YOUR_DB_PORT"
)

# Redis connection
redis_client = redis.Redis(
    host='YOUR_REDIS_HOST',
    port=YOUR_REDIS_PORT,
    password='YOUR_REDIS_PASSWORD'
)

@app.route('/player-data', methods=['POST'])
def player_data():
    data = request.json
    player_id = data.get('playerId')
    player_name = data.get('playerName')
    wallet_address = data.get('walletAddress')

    # تخزين البيانات في PostgreSQL
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO players (id, name, wallet) VALUES (%s, %s, %s)",
        (player_id, player_name, wallet_address)
    )
    conn.commit()

    # تخزين حالة التعدين في Redis
    redis_client.set(f'player:{player_id}:mining', 'active')

    return jsonify({"message": "تم استقبال البيانات بنجاح!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
