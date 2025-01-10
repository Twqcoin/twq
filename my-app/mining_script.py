import time

def start_mining(user_id):
    # هنا يتم تنفيذ عملية التعدين
    print(f"Starting mining for user {user_id}")
    while True:
        # عملية التعدين تستمر حتى يتوقف
        time.sleep(60)
        print(f"Mining for {user_id} is ongoing...")

if __name__ == "__main__":
    start_mining("user123")
