import calendar
from datetime import datetime

def get_isodate(start_month, end_month, year):
    end_day = calendar.monthrange(year, end_month)[1]
    start = datetime(year, start_month, 1).isoformat()
    end = datetime(year, end_month, end_day).isoformat()
    return start, end

def get_quarters(year):
    today = datetime.today().isoformat()
    quarters = [(x, x+2) for x in range(1, 12, 3)]
    dates = [get_isodate(start, end, year) for (start, end) in quarters]
    valid_dates = [date for date in dates if today >= date[1]]
    
    return valid_dates

def get_params(cursor, _from, _to, topic, first=125):
    print("param topic")
    print(topic)
    params = {
        "settings": {
            "after": cursor,
            "first": first,
            "events": {
                "time": {
                    "from": _from,
                    "to": _to,
                },
                "languages": "ENGLISH",
                "topics": topic
            }
        },
        "language": "ENGLISH",
    }
    return params
