import datetime
import os

class Logger():
    def __init__(self):
        f1 = "./Logs/logs.txt"
        # Create Logs directory if it does not exist
        if not os.path.exists(f1):
            os.makedirs(os.path.dirname(f1), exist_ok=True)
            with open(f1, "w") as f:
                data = 0
                f.write(str(data))
                f.close()
        else:
            with open(f1, "r+") as f:
                data = int(f.read())
                f.seek(0)
                f.write(str(data + 1))
                f.truncate()
                f.close()
        file = "./Logs/log" + str(data) + ".txt"
        # os.makedirs(os.path.dirname(file), exist_ok=True)
        self.log = open(file, "w")
        self.log.write(f"Log {data}\n")

    def write(self, data):
        self.log.write(f"{datetime.datetime.now()} {data}\n")

    def close(self):
        self.log.close()
