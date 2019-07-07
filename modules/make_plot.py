import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64


def generate_base64_datetime_plot(x_datetimes, y_data, title='', xlabel='', ylabel=''):

    # Build Graph
    plt.plot(x_datetimes, y_data)

    # Handle Dates
    date_format = mdates.DateFormatter('%d/%m %H:%M')
    plt.gca().xaxis.set_major_formatter(date_format)

    # Graph Info
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.gcf().autofmt_xdate()

    # Build Image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()

    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')

    return 'data:image/png;base64,' + graph_url


def generate_base64_plot(x_data, y_data, title='', xlabel='', ylabel=''):
    # build graph
    plt.plot(x_data, y_data)

    # graph info
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # build image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()

    img.seek(0)
    graph = base64.b64encode(img.getvalue()).decode('utf8')

    return 'data:image/png;base64,' + graph
