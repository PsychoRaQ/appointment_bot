from lexicon.lexicon import DATE_LST


async def change_datetime_status(datetime) -> None:
    date, time = datetime.split(',')

    if date in DATE_LST:
        DATE_LST[date].times[time].lock = True
