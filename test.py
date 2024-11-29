import datetime

ran = 30


res = [(datetime.datetime.combine(datetime.date.today(), datetime.time(0,0)) + datetime.timedelta(minutes=i)).time().strftime("%H:%M")
       for i in range(0, 24*60, ran)]

print(res)