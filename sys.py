import os
import psutil
import platform

from demo_opts import get_device
from luma.core.render import canvas

from PIL import ImageFont, ImageDraw

import time
from datetime import datetime


global line1
line1=2
global line2
line2=12
global line3
line3=20
global col1
col1=4


def do_nothing(obj):
    pass

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)

device = get_device()

device.cleanup = do_nothing



font10 = ImageFont.load_default()


 
byteunits = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
def filesizeformat(value):
    exponent = int(log(value, 1024))
    return "%.1f %s" % (float(value) / pow(1024, exponent), byteunits[exponent])
 
def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n
  
def cpu_usage():
    # load average, uptime
    av1, av2, av3 = os.getloadavg()
    tempC = ((int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000))
    return "LOAD: %.1f %.1f %.1f" \
        % (av1, av2, av3)
 
def cpu_temperature():
    # load average, uptime
    av1, av2, av3 = os.getloadavg()
    tempC = ((int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000))
    return "CPU TEMP: %sc" \
        % (str(tempC))
 
def mem_usage():
    usage = psutil.virtual_memory()
    return "MEM FREE: %s/%s" \
        % (bytes2human(usage.available), bytes2human(usage.total))
  
def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "DSK FREE: %s/%s" \
        % (bytes2human(usage.total-usage.used), bytes2human(usage.total))
  
def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "NET: %s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))
  
def lan_ip():
    f = os.popen('ifconfig eth0 | grep "inet " | cut -c 14-26')
    #f = os.popen("ip route get 1 | awk '{print $NF;exit}'")
    ip = str(f.read())
    # strip out trailing chars for cleaner output
    return "IP: %s" % ip.rstrip('\r\n').rstrip(' ')

def stats():
    global looper
    with canvas(device) as draw:
        draw.rectangle((0,0,127,63), outline="white", fill="black")
        if looper==0:
            draw.text((col1, line1), 'OPi ZERO', font=font10, fill=255)
            draw.text((col1, line3), 'Starting up...', font=font10, fill=255)
            looper=1
        elif looper==1:
            draw.text((col1, line1), cpu_usage(),  font=font10, fill=255)
            draw.text((col1, line2), cpu_temperature(),  font=font10, fill=255)
            looper=2
        elif looper==2:
            draw.text((col1, line1), mem_usage(),  font=font10, fill=255)
            draw.text((col1, line2), disk_usage('/'),  font=font10, fill=255)
            looper=3       
        elif looper==3:
            draw.text((col1, line1),"%s %s" % (platform.system(),platform.release()), font=font10, fill=255)
            draw.text((col1, line2), lan_ip(),  font=font10, fill=255)
            looper=4
        else:
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            draw.text((col1, line1),str(datetime.now().strftime('%a %b %d %H:%M:%S')), font=font10, fill=255)
            draw.text((col1, line2),"%s" % str(uptime).split('.')[0], font=font10, fill=255)
            looper=1
    
def main():
    global looper
    looper = 0
    while True:
        stats()
        if looper==0:
            time.sleep(7)
        else:
            time.sleep(3)
  
  
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

