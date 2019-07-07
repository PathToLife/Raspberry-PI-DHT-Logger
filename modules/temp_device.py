import Adafruit_DHT


def get_temp(pin=17):
    sensor = Adafruit_DHT.DHT22
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    humidity = round(humidity, 5)
    temperature = round(temperature, 5)

    if humidity is not None and temperature is not None and humidity < 1000:
        # print("Temp={0:0.1f}°C Humidity={1:0.1f}%".format(temperature, humidity))
        return humidity, temperature
    else:
        return -1, -1


if __name__ == '__main__':
    h, t = get_temp()
    print("Temp={0:0.1f}°C Humidity={1:0.1f}%".format(t, h))
