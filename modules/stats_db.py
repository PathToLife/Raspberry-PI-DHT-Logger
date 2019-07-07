import sqlite3
from datetime import datetime, timedelta

DATABASE_FILENAME = 'TM_data.sqlite'


class Stats:
    db_key = 'stats'

    page_views = 0
    temp = -1
    humid = -1

    avg_temp = -1
    num_temp = 0
    temp_record = []

    avg_humid = -1
    num_humid = 0
    humid_record = []

    cpu_percent = 0

    error_count = 0

    def add_temp(self, temp: float):
        cumulative_temp = self.avg_temp * self.num_temp + temp
        self.avg_temp = cumulative_temp / (self.num_temp + 1)
        self.num_temp += 1
        self.temp_record.append(temp)
        self.temp = temp

    def add_humid(self, humid: float):
        cumulative_humid = self.avg_humid * self.num_humid + humid
        self.avg_humid = cumulative_humid / (self.num_humid + 1)
        self.num_humid += 1
        self.humid_record.append(humid)
        self.humid = humid
        # print(self.humid_record, self.avg_humid ,self.num_humid, cumulative_humid)

    def error_increment(self):
        self.error_count += 1


def execute(sql, values=()):
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    c.execute(sql, values)
    c.close()
    db.commit()
    db.close()


def fetchall(sql, values=()):
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    c.execute(sql, values)
    data = c.fetchall()
    c.close()
    db.close()
    return data


def create_tables():
    # language=sql
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS dht_table (
        id integer PRIMARY KEY,
        temperature float NOT NULL,
        humidity float NOT NULL,
        recorded_date date NOT NULL
        )''',
        '''
        CREATE TABLE IF NOT EXISTS cpu_table (
            id integer PRIMARY KEY,
            percent float NOT NULL,
            recorded_date date NOT NULL
        )'''
    ]
    for s in tables:
        execute(s)


def record_dht(temp, humid, recorded_date=None):
    # language=sql
    s = '''INSERT INTO dht_table(temperature, humidity, recorded_date) VALUES (?, ?, ?)'''
    if recorded_date is None:
        recorded_date = datetime.today()
    execute(s, (temp, humid, recorded_date))


def fetch_dht_all():
    # language=sql
    s = '''SELECT * FROM dht_table WHERE temperature > 0'''
    return fetchall(s)


def fetch_dht_range(t1, t2):
    s = '''SELECT * FROM dht_table WHERE recorded_date > ? and recorded_date < ? and temperature > 0'''
    return fetchall(s, (t1, t2))


def get_dht_errors():
    # language=sql
    s = '''SELECT * FROM dht_table WHERE temperature == -1'''
    return fetchall(s)


def fetch_cpu_all():
    # language=sql
    s = '''SELECT * FROM cpu_table'''
    return fetchall(s)


def clear_dht_table():
    # language=sql
    s = '''DELETE FROM dht_table WHERE 1'''
    execute(s)


def clear_cpu_table():
    # language=sql
    s = '''DELETE FROM cpu_table WHERE 1'''
    execute(s)


def record_cpu(percent, recorded_date=None):
    # language=sql
    if recorded_date is None:
        recorded_date = datetime.today()
    s = '''INSERT INTO cpu_table(percent, recorded_date) VALUES (?, ?)'''
    execute(s, (percent, recorded_date))


def get_datetime(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")


def del_errored():
    # language=sql
    s = '''DELETE FROM dht_table where humidity > 1000'''
    execute(s)


create_tables()
del_errored()

if __name__ == '__main__':
    from pprint import pprint
    # clear_dht_table()
    times = fetch_dht_all()
    pprint(times)
