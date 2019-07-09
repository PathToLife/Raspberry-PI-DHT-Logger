from flask import Flask, render_template, send_from_directory
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import subprocess
from sys import platform

from modules import stats_db, make_plot
from modules import temp_device

# Init oled display if installed
from modules import oled_display

cron = BackgroundScheduler()
app = Flask(__name__)

current_temp = (-1, -1)
current_page_views_counter = 0
stats = stats_db.Stats()


def get_text_dict():

    text_dict = {
        'temp_str': "{:.1f}°C AVG {:.1f}°C".format(stats.temp, stats.avg_temp),
        'humid_str': "{:.1f}% AVG {:.1f}%".format(stats.humid, stats.avg_humid),
        'time_str': datetime.datetime.now().strftime('%I:%M:%S%p %d/%m'),
        'cpu_str': str(stats.cpu_percent) + "%",
        'current_page_views': "Views: " + str(current_page_views_counter)
    }

    return text_dict


def get_cpu():
    cmd = None
    s = -1
    if platform == "linux" or platform == "linux2":
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    elif platform == 'darwin':
        cmd = "top -l 1 | grep Load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"

    if cmd is not None:
        s = subprocess.check_output(cmd, shell=True).decode("utf-8")
        s = s.strip()
        s = s[len('CPU Load: '):]
    try:
        return float(s)
    except ValueError:
        return -1


@cron.scheduled_job(trigger='interval', seconds=12, max_instances=1)
def get_data():
    global stats
    stats.humid, stats.temp = temp_device.get_temp(17)

    stats_db.record_dht(stats.temp, stats.humid)
    stats.cpu_percent = get_cpu()
    stats_db.record_cpu(stats.cpu_percent)


if oled_display.display is not None:
    @cron.scheduled_job(trigger='interval', seconds=12, max_instances=1)
    def draw_display():
        key_order = [
            'temp_str', 'humid_str', 'time_str', 'cpu_str', 'current_page_views'
        ]
        oled_display.draw_display(stats, get_text_dict(), key_order)


cron.start()


@app.route('/<path:filename>')
def send_public_file(filename):
    return send_from_directory('public/', filename)


@app.route('/')
def main_page():
    global current_page_views_counter
    current_page_views_counter += 1
    text_dict = get_text_dict()

    dht_data = stats_db.fetch_dht_all()
    temp_x = [x[3] for x in dht_data]
    temp_y = [x[1] for x in dht_data]
    humid_x = temp_x
    humid_y = [x[2] for x in dht_data]

    cpu_data = stats_db.fetch_cpu_all()
    cpu_x = [x[0] for x in cpu_data]
    cpu_y = [x[1] for x in cpu_data]

    stats_dict = {
        'temp_x': temp_x,
        'temp_y': temp_y,
        'humid_x': humid_x,
        'humid_y': humid_y,
        'cpu_x': cpu_x,
        'cpu_y': cpu_y
    }

    return render_template('main.html', **stats_dict, **text_dict)


def safe_exit():
    oled_display.close()
    print('Exit Called')


atexit.register(lambda: cron.shutdown(wait=False))
atexit.register(lambda: safe_exit())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
