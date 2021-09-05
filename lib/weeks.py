from datetime import date, timedelta

def get_weeks_list():
    dates = []
    week_length = 7
    number_of_weeks = 13
    first_monday = date(2021,2,22) 
    for i in range(0, number_of_weeks):
        monday = first_monday+ timedelta(days = i*week_length)
        sunday = (monday + timedelta(days = week_length-1))
        parameters = {
            "_start": f"{monday} 00:00:00",
            "_end": f"{sunday} 23:59:59"
        }
        dates.append(parameters)

    return dates