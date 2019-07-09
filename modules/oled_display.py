try:
    import Adafruit_SSD1306
    display = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
except ImportError:
    Adafruit_SSD1306 = None
    display = None


if display is not None:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    display.begin()
    display.clear()
    display.display()

    width = display.width
    height = display.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # font = ImageFont.load_default()
    fontSize = 12
    font = ImageFont.truetype('tahoma.ttf', fontSize)


def draw_display(stats, text_dict, key_order):

    if display is None:
        print('Display does not exist, ignoring draw')
        return

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

    for k in key_order:
        draw.text((x, y), text_dict.get(k, ''), font=font, fill=255)
        y += fontSize

    # Display image
    display.image(image)
    display.display()


def close():
    if display is None:
        print('Display does not exist, ignoring close')
        return

    display.clear()
    display.display()
