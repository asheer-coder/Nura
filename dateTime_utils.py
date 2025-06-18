import time

def get_date():
    return time.strftime("%d/%m/%Y", time.localtime())

def get_time():
    return time.strftime("%H:%M:%S %p", time.localtime())