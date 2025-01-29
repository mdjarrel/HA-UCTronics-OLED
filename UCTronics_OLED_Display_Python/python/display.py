# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

## REF https://pillow.readthedocs.io/

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!
import math
from os import stat
import time
import sys, getopt
import subprocess
import json
import logging
logger = logging.getLogger(__name__)

from PIL import Image, ImageDraw, ImageFont, ImageOps
import uctronics

## Global Variables
# Default set, but can be overridden by config in addon setup.
TEMP_UNIT = "C"
SHOW_SPLASH = True
SHOW_CPU = True
SHOW_NETWORK = True
SHOW_MEMORY = True
SHOW_STORAGE = True
DURATION = 5

HEADER_Y_OFFSET = 32

MAX_WIDTH = 160
MAX_HEIGHT = 80

PADDING_THIN = 2
PADDING = 4
ICON_W = 32
ICON_H = ICON_W
START = ICON_W + (2 * PADDING)

def start():
    while True:
        pageDisp = False
        show_header()
        try:
            if (SHOW_SPLASH):
                show_splash()
                pageDisp = True
        except:
            logger.error(sys.exception())
        try:
            if (SHOW_CPU):
                show_cpu_temp()
                pageDisp = True
        except:
            logger.error(sys.exception())
        try:
            if (SHOW_MEMORY):
                show_memory()
                pageDisp = True
        except:
            logger.error(sys.exception())
        try:
            if (SHOW_NETWORK):
                show_network()
                pageDisp = True
        except:
            logger.error(sys.exception())
        try:
            if (SHOW_STORAGE):
                show_storage()
                pageDisp = True
        except:
            logger.error(sys.exception())
        if not pageDisp:
            time.sleep(1)

def show_storage():
    storage =  shell_cmd('df -h | awk \'$NF=="/"{printf "%d,%d,%s", $3,$2,$5}\'')
    storage = storage.split(',')

    # Clear Canvas
    draw.rectangle((0,HEADER_Y_OFFSET,width,height), outline=0, fill=0)

    # Resize and merge icon to Canvas
    icon = img_disk.resize([ICON_W,ICON_H])  
    image.paste(icon,(PADDING,HEADER_Y_OFFSET + PADDING))

    ln1 = 'USED: ' + storage[0] + ' GB'
    ln2 = 'TOTAL: ' + storage[1] + ' GB'
    ln3 = 'UTILISED: ' + storage[2]
    
    ln1_w = draw.textlength(ln1, font=small)
    ln2_w = draw.textlength(ln2, font=small)
    ln3_w = draw.textlength(ln2, font=small)
    
    ln_longest = max([ln1_w,ln2_w,ln3_w])
    
    ln_x = (width - PADDING) - ln_longest
    
    ln = ''
    for line in [ln1,ln2,ln3]:
        ln += line + '\n'
    
    draw.multiline_text((START,HEADER_Y_OFFSET + PADDING), ln, font=small, fill=(255,255,255))

    #image.save(r"./img/examples/storage.png")    

    disp.image(data=image)
    disp.show()
    time.sleep(DURATION)  

def show_memory():
    mem = shell_cmd("free -m | awk 'NR==2{printf \"%.1f,%.1f,%.0f%%\", $3/1000,$2/1000,$3*100/$2 }'")
    mem = mem.split(',')

    # Clear Canvas
    draw.rectangle((0,HEADER_Y_OFFSET,width,height), outline=0, fill=0)

    # Resize and merge icon to Canvas
    icon = img_mem.resize([ICON_W,ICON_H])  
    image.paste(icon,(PADDING,HEADER_Y_OFFSET + PADDING))

    ln1 = 'USED: ' + mem[0] + ' GB'
    ln2 = 'TOTAL: ' + mem[1] + ' GB'
    ln3 = 'UTILISED: ' + mem[2]
    
    ln1_w = draw.textlength(ln1, font=small)
    ln2_w = draw.textlength(ln2, font=small)
    ln3_w = draw.textlength(ln2, font=small)
    
    ln_longest = max([ln1_w,ln2_w,ln3_w])
    
    ln_x = (width - PADDING) - ln_longest
    
    ln = ''
    for line in [ln1,ln2,ln3]:
        ln += line + '\n'
    
    draw.multiline_text((START,HEADER_Y_OFFSET + PADDING), ln, font=small, fill=(255,255,255))

    #image.save(r"./img/examples/memory.png")   

    disp.image(data=image)
    disp.show()
    time.sleep(DURATION) 


def show_cpu_temp():
    #host_info = hassos_get_info('host/info')

    cpu = shell_cmd("top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'")
    temp =  float(shell_cmd("cat /sys/class/thermal/thermal_zone0/temp")) / 1000.00
    uptime = shell_cmd("uptime | grep -ohe 'up .*' | sed 's/,//g' | awk '{ print $2" "$3 }'")

    # Check temapture unit and convert if required.
    if (TEMP_UNIT == 'C'): 
        temp = "%0.2f °C " % (temp)
    else:
        temp = "%0.2f °F " % (temp * 9.0 / 5.0 + 32)


    # Clear Canvas
    draw.rectangle((0,HEADER_Y_OFFSET,width,height), outline=0, fill=0)

    # Resize and merge icon to Canvas
    icon = img_cpu_64.resize([ICON_W,ICON_H])  
    image.paste(icon,(PADDING,HEADER_Y_OFFSET + PADDING))

    ln1 = 'TEMP: ' + temp
    ln2 = 'LOAD: '+ cpu + '%'
    ln3 = 'UPTIME: ' + uptime.upper()
    
    ln1_w = draw.textlength(ln1, font=small)
    ln2_w = draw.textlength(ln2, font=small)
    ln3_w = draw.textlength(ln2, font=small)
    
    ln_longest = max([ln1_w,ln2_w,ln3_w])
    
    ln_x = (width - PADDING) - ln_longest
    
    ln = ''
    for line in [ln1,ln2,ln3]:
        ln += line + '\n'
    
    draw.multiline_text((START,HEADER_Y_OFFSET + PADDING), ln, font=small, fill=(255,255,255))

    #image.save(r"./img/examples/cpu.png")
    
    disp.image(data=image)
    disp.show()
    time.sleep(DURATION)


def show_network():
    host_info = hassos_get_info('host/info')
    logger.info(str(host_info))
    hostname = host_info['data']['hostname'].upper()

    network_info = hassos_get_info('network/info')
    #logger.info(str(network_info))
    ipv4 = 'xxx.xxx.xxx.xxx'
    try:
        for interface in network_info['data']['interfaces']:
            if interface['primary']:
                ipv4 = interface['ipv4']['address'][0].split("/")[0]
    except:
        pass
    mac = 'XX:XX:XX:XX:XX:XX'
    try:
        for interface in network_info['data']['interfaces']:
            if interface['primary']:
                mac = interface['mac']
    except:
        pass

    # Clear Canvas
    draw.rectangle((0,HEADER_Y_OFFSET,width,height), outline=0, fill=0)

    # Resize and merge icon to Canvas
    icon = img_network.resize([ICON_W,ICON_H])  
    image.paste(icon,(PADDING,HEADER_Y_OFFSET + PADDING))

    #ln1 = 'HOST: ' + hostname
    #ln2 = 'IP4: '+ ipv4
    ln3 = 'MAC: ' + mac.upper()
    
    #ln1_w = draw.textlength(ln1, font=small)
    #ln2_w = draw.textlength(ln2, font=small)
    ln3_w = draw.textlength(ln2, font=small)
    
    #ln_longest = max([ln1_w,ln2_w,ln3_w])
    
    #ln_x = (width - PADDING) - ln_longest
    
    #ln = ''
    #for line in [ln1,ln2,ln3]:
    #    ln += line + '\n'
    
    draw.multiline_text((START,HEADER_Y_OFFSET + PADDING), ln3+'\n', font=small, fill=(255,255,255))

    #image.save(r"./img/examples/network.png")

    disp.image(data=image)
    disp.show()
    time.sleep(DURATION)

def get_text_center(text, font, center_point):
    w = draw.textlength(text, font=font)
    return (center_point -(w/2))


def show_splash():
    os_info = hassos_get_info('os/info')    
    os_version = os_info['data']['version']
    os_upgrade = os_info['data']['update_available']  
    if (os_upgrade == True):
        os_version = os_version + "*"

    core_info = hassos_get_info('core/info')
    core_version = core_info['data']['version']  
    core_upgrade = os_info['data']['update_available']
    if (core_upgrade == True):
        core_version =  core_version + "*"

    # Clear Canvas
    draw.rectangle((0,HEADER_Y_OFFSET,width,height), outline=0, fill=0)

    # Get HA Logo and Resize
    logo = img_ha_logo.resize([32,32])
    logo = ImageOps.invert(logo)  
    
    # Merge HA Logo with Canvas.
    image.paste(logo,(PADDING,HEADER_Y_OFFSET + PADDING)) # (-2,3)

    ln1 = "Home Assistant"
    ln2 = 'OS '+ os_version + ' - ' + core_version
    
    ln1_w = draw.textlength(ln1, font=p_bold)
    ln2_w = draw.textlength(ln2, font=small)
    
    ln_longest = max([ln1_w,ln2_w])
    
    ln_center = ((width - PADDING) - ln_longest) + (ln_longest / 2)
    
    #logger.info('Longest: ' + str(ln_longest))
    #logger.info('Center: ' + str(ln_center))
    
    ln1_x = get_text_center(ln1, p_bold, ln_center) #78
    draw.text((ln1_x, HEADER_Y_OFFSET + 4), ln1, font=p_bold, fill=(255,255,255))
    
    #draw.line([(34, 16),(123,16)], fill=255, width=1)
    draw.line([(ln1_x, HEADER_Y_OFFSET + 20),((width - PADDING),HEADER_Y_OFFSET + 20)], fill=(0x94,0x82,0x94), width=1) #948294
    
    ln2_x = get_text_center(ln2, small, ln_center) #78
    draw.text((ln2_x, HEADER_Y_OFFSET + 22), ln2, font=small, fill=(0xa5,0x20,0xff)) #a520ff

    # Display Image to OLED
    #image.save(r"./img/examples/splash.png")
    disp.image(data=image)
    disp.show() 
    time.sleep(DURATION)
    
def show_header():
    host_info = hassos_get_info('host/info')
    logger.info(str(host_info))
    hostname = host_info['data']['hostname']

    network_info = hassos_get_info('network/info')
    #logger.info(str(network_info))
    ipv4 = 'xxx.xxx.xxx.xxx'
    try:
        for interface in network_info['data']['interfaces']:
            if interface['primary']:
                ipv4 = interface['ipv4']['address'][0].split("/")[0]
    except:
        pass
    mac = 'XX:XX:XX:XX:XX:XX'
    try:
        for interface in network_info['data']['interfaces']:
            if interface['primary']:
                mac = interface['mac']
    except:
        pass
    
    ln1 = 'HOST: ' + hostname
    ln2 = 'IP4: '+ ipv4
    #ln3 = 'MAC: ' + mac.upper()

    
    ln = ''
    for line in [ln1,ln2]:
        ln += line + '\n'
        
    left, top, right, bottom = draw.multiline_textbbox((0,0), ln, font=small)
    global HEADER_Y_OFFSET
    HEADER_Y_OFFSET = bottom + (2*PADDING_THIN)
    
    # Clear Header Canvas
    draw.rectangle((0,0,width,HEADER_Y_OFFSET), outline=0, fill=(0xc8,0xc8,0xc8))
    
    draw.multiline_text((PADDING_THIN,PADDING_THIN), ln, font=small, fill=(0,0,0))

def hassos_get_info(type):
    info = shell_cmd('curl -sSL -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/' + type)
    return json.loads(info)


def shell_cmd(cmd):
    result = ''
    try:
        result = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except:
        logger.error(sys.exception())
    finally:
        return result


def get_options():
    f = open("/data/options.json", "r")
    options = json.loads(f.read())
    f.close()
    global TEMP_UNIT, SHOW_SPLASH, SHOW_CPU, SHOW_MEMORY, SHOW_STORAGE, SHOW_NETWORK, DURATION
    TEMP_UNIT = options['Temperature_Unit']
    SHOW_SPLASH = options['Show_Splash_Screen']
    SHOW_CPU = options['Show_CPU_Info']
    SHOW_MEMORY =options['Show_Memory_Info']
    SHOW_STORAGE = options['Show_Storage_Info']
    SHOW_NETWORK = options['Show_Network_Info']
    DURATION =  options['Slide_Duration']

def clear_display():
    disp.fill(0)
    disp.show()

logging.basicConfig(level=logging.INFO)

# Create the UC-B86 class.
# The first two parameters are the pixel width and pixel height.  Change these to the right size for your display!
disp = uctronics.UCB86(MAX_WIDTH, MAX_HEIGHT)
logger.info('Created disp')

# Clear display.
clear_display()
logger.info('Cleared disp')

# Create blank image for drawing.

width = disp.width
height = disp.height

image = Image.new("RGB", (width, height))
logger.info('Created img')

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
logger.info('Created canvas')

# Load default font.
# font = ImageFont.load_default()
p = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 13)
p_bold = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 13)
small = ImageFont.truetype("usr/share/fonts/dejavu/DejaVuSans.ttf", 11)
smaller = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 10)
logger.info('Loaded fonts')


img_network = Image.open(r"./img/ip-network.png")
img_mem = Image.open(r"./img/database.png")
img_disk = Image.open(r"./img/database-outline.png")
img_ha_logo = m = Image.open(r"./img/home-assistant-logo.png")
img_cpu_64 = Image.open(r"./img/cpu-64-bit.png")
logger.info('Loaded imgs')

if __name__ == "__main__":
    logger.info('Getting options')
    get_options()
    logger.info('Starting routine')
    start()
    logger.info('Closing disp')
    disp.close()
    logger.info('Done')
