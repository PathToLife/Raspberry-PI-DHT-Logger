from flask import Flask, render_template_string, send_from_directory
from modules import stats_db, make_plot

app = Flask(__name__)


@app.route('/<path:filename>')
def send_public_file(filename):
    return send_from_directory('public/', filename)


@app.route('/')
def index():
    # language=html
    template = '''
    <html lang="en">
    <head>
        <title>Test Scripts</title>
        <script src="plotly-latest.min.js"></script>
    </head>
    <body>
        <div>{{ sys_info }}</div>
        <div id="temp-humid-graph" style="width:800px;height:400px;"></div>
        <img src="{{ plot1 }}" alt="plot1"/>
        <img src="{{ plot2 }}" alt="plot2"/>
        <img src="{{ plot3 }}" alt="plot3"/>
        
        <script>
            var elem = document.getElementById('temp-humid-graph');
            
            Plotly.plot(
            elem,
            [{
            x: {{ temp_x }},
            y: {{ temp_y }}
            },
            {
            x: {{ humid_x }},
            y: {{ humid_y }}
            }
            ], {
            margin: { t: 0 } } );
	    </script>
    </body>

    </html>
    '''
    data1 = stats_db.fetch_dht_all()
    info = str(len(data1))
    x = [x[0] for x in data1]
    y_temp = [x[1] for x in data1]
    y_humid = [x[2] for x in data1]
    plot1 = make_plot.generate_base64_plot(x, y_temp, 'Temperature', 'time', 'C')
    plot2 = make_plot.generate_base64_plot(x, y_humid, "Humidity", "time", "%")

    data2 = stats_db.fetch_cpu_all()
    x2 = [x[0] for x in data2]
    y_cpu = [x[1] for x in data2]
    plot3 = make_plot.generate_base64_plot(x2, y_cpu, 'Cpu', 'time', '%')
    return render_template_string(template, sys_info=info, plot1=plot1, plot2=plot2, plot3=plot3,
                                  temp_x=str(x), temp_y=str(y_temp), humid_x=str(x), humid_y=str(y_humid))


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


app.run('localhost', 8000)