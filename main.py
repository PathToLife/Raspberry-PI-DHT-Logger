from flask import Flask, render_template_string, send_from_directory
import matplotlib.pyplot as plt
import io
import base64
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

from modules import stats_db, make_plot
from modules import temp_device

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

cron = BackgroundScheduler()
app = Flask(__name__)

RST = None
display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
display.begin()
display.clear()
display.display()

width = display.width
height = display.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)
draw.rectangle((0, 0, width, height), outline=0, fill=0)

current_temp = (-1, -1)
current_page_views_counter = 0


stats = stats_db.Stats()


class Html:
    # language=html
    template = '''
    <!DOCTYPE html>
    <html lang="EN">
    <head>
        <title>TempMonitor</title>
        <link rel="stylesheet" type="text/css" href="styles.css"
    </head>
    <body>
        <div>
            <span><a href="/graph">Graphs</a></span>
        </div>
        <div>Temp: {{ temp_str }}</div>
        <div>Temp: {{ humid_str }}</div>
        <div>Time: {{ time_str }}</div>
        <div>{{ cpu_str }}</div>
        <div>{{ current_page_views }}</div>
    </body>
    </html>
    '''

    @staticmethod
    def generate_base64_plot(x_data, y_data):
        img = io.BytesIO()
        plt.plot(x_data, y_data)
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode('utf8')
        return 'data:image/png;base64,' + graph_url


def get_text_dict():

    text_dict = {
        'temp_str': "{:.1f}°C AVG {:.1f}°C".format(stats.temp, stats.avg_temp),
        'humid_str': "{:.1f}% AVG {:.1f}%".format(stats.humid, stats.avg_humid),
        'time_str': datetime.datetime.now().strftime('%I:%M:%S%p %d/%m'),
        'cpu_str': str(stats.cpu_percent) + "%",
        'current_page_views': "Views: " + str(current_page_views_counter)
    }

    return text_dict


# font = ImageFont.load_default()
fontSize = 12
font = ImageFont.truetype('tahoma.ttf', fontSize)


@cron.scheduled_job(trigger='interval', seconds=12, max_instances=1)
def draw_display():
    global stats
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    x = 0
    y = 0

    # Shell scripts for system monitoring from here :
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    # cmd = "hostname -I | cut -d\' \' -f1"
    # IP = subprocess.check_output(cmd, shell=True)
    # cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    # CPU = subprocess.check_output(cmd, shell=True)
    # cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    # MemUsage = subprocess.check_output(cmd, shell=True)
    # cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    # Disk = subprocess.check_output(cmd, shell=True)

    # Write two lines of text.

    text_dict = get_text_dict()
    key_order = [
        'temp_str', 'humid_str', 'time_str', 'cpu_str', 'current_page_views'
    ]

    for k in key_order:
        draw.text((x, y), text_dict.get(k, ''), font=font, fill=255)
        y += fontSize

    # Display image
    display.image(image)
    display.display()


def get_cpu():
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    s = subprocess.check_output(cmd, shell=True).decode("utf-8")
    s = s.strip()
    s = s[len('CPU Load: '):]
    try:
        return float(s)
    except ValueError:
        return -1


@cron.scheduled_job(trigger='interval', seconds=3, max_instances=1)
def get_data():
    global stats
    stats.humid, stats.temp = temp_device.get_temp(17)

    stats_db.record_dht(stats.temp, stats.humid)
    stats.cpu_percent = get_cpu()
    stats_db.record_cpu(stats.cpu_percent)


cron.start()


@app.route('/<path:filename>')
def send_css(filename):
    return send_from_directory('public/', filename)


@app.route('/')
def main_page():
    global current_page_views_counter
    current_page_views_counter += 1
    text_dict = get_text_dict()

    return render_template_string(Html.template,
                                  **text_dict)


@app.route('/graph')
def index():
    # language=html
    template = '''
    <!DOCTYPE html>
    <html lang="en">
    <body>
        <div>
            <span><a href="/">Home</a></span>
            <span>{{ sys_info }}</span>
        </div>
        <img src="{{ plot1 }}" alt="plot1"/>
        <img src="{{ plot2 }}" alt="plot2"/>
        <img src="{{ plot3 }}" alt="plot3"/>
    </body>

    </html>
    '''
    data1 = stats_db.fetch_dht_all()
    info = "Entries Loaded: " + str(len(data1))
    # x = [x[0] for x in data1]
    x = [stats_db.get_datetime(x[3]) for x in data1]
    y_temp = [x[1] for x in data1]
    y_humid = [x[2] for x in data1]
    plot1 = make_plot.generate_base64_datetime_plot(x, y_temp, 'Temperature', 'time', 'C')
    plot2 = make_plot.generate_base64_datetime_plot(x, y_humid, "Humidity", "time", "%")

    data2 = stats_db.fetch_cpu_all()
    #  x2 = [x[0] for x in data2]
    x2 = [stats_db.get_datetime(x[2]) for x in data2]
    y_cpu = [x[1] for x in data2]
    plot3 = make_plot.generate_base64_datetime_plot(x2, y_cpu, 'Cpu', 'time', '%')
    return render_template_string(template, sys_info=info, plot1=plot1, plot2=plot2, plot3=plot3)


def safe_exit():
    display.clear()
    display.display()
    print('Exit Called')


atexit.register(lambda: cron.shutdown(wait=False))
atexit.register(lambda: safe_exit())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
