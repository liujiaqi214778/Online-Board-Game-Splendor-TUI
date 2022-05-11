# 2022/5/11  23:49  liujiaqi
import queue
import time

LOG = False
LOGFILENAME = time.asctime().replace(" ", "_").replace(":", "-")
logQ = queue.Queue()


# A thread to log all the texts. Flush from logQ.
def logThread():
    global logQ
    while True:
        time.sleep(1)
        with open("SERVER_LOG_" + LOGFILENAME + ".txt", "a") as f:
            while not logQ.empty():
                data = logQ.get()
                if data is None:
                    return
                else:
                    f.write(data)


# A function to Log/Print text. Used instead of print()
def log(data, key=None, adminput=False):
    global logQ
    if adminput:
        text = ""
    elif key is None:
        text = "SERVER: "
    else:
        text = f"Player {key}: "

    if data is not None:
        text += data
        if not adminput:
            print(text)

        if LOG:
            logQ.put(time.asctime() + ": " + text + "\n")
    else:
        logQ.put(None)
