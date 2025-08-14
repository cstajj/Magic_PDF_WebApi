from datetime import datetime

def getDateTime()->str:
    now = datetime.now()
    format_string = "%Y-%m-%d %H:%M:%S"
    formatted_datetime_string = now.strftime(format_string)
    return formatted_datetime_string