import time
import random
import board

import rotaryio
import digitalio

import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

import displayio
import terminalio
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import adafruit_displayio_sh1106

import gc
gc.collect()

m = Mouse(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)

button = digitalio.DigitalInOut(board.D0)
button.direction = digitalio.Direction.INPUT
encoder = rotaryio.IncrementalEncoder(board.A1, board.A2)

WIDTH = 128
HEIGHT = 64
BORDER = 0

displayio.release_displays()

i2c = board.I2C()
display_bus = I2CDisplayBus(i2c, device_address=0x3C)

display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)
display.rotation = 180

#gc.collect()
#start_mem = gc.mem_free()
#print( "Point 1 Available memory: {} bytes".format(start_mem) )

root_group = displayio.Group()
display.root_group = root_group

menu_group = displayio.Group()
root_group.append(menu_group)

foreground_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
foreground_palette = displayio.Palette(1)
foreground_palette[0] = 0x000000
foreground_sprite = displayio.TileGrid(foreground_bitmap, pixel_shader=foreground_palette, x=BORDER, y=BORDER)
menu_group.append(foreground_sprite)

selection_bitmap = displayio.Bitmap(WIDTH, 20, 1)
selection_palette = displayio.Palette(1)
selection_palette[0] = 0xFFFFFF
selection_sprite = displayio.TileGrid(selection_bitmap, pixel_shader=selection_palette, x=0, y=HEIGHT - 43)
menu_group.append(selection_sprite)

text = ""
previous_label = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=12, y=HEIGHT - 50)
selected_label = label.Label(terminalio.FONT, text=text, color=0x000000, x=12, y=HEIGHT // 2 - 1, scale=2)
next_label = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=12, y=HEIGHT - 14)

menu_group.append(previous_label)
menu_group.append(selected_label)
menu_group.append(next_label)

options = ["Off", "Jiggle", "Click", "Jump", "Walk", "Game"]
selection_index = 0
prev_option = 0
next_option = 0

is_awake = True
def sleep():
    display_bus.send(0xAE, bytearray())

def wake():
    display_bus.send(0xAF, bytearray())

run_frames = (0,5)
sit_frames = (6,9)
lay_frames = (10,12)
sleep_frames = (13,20)
previous_frame = 0

cat_frames = (
    displayio.OnDiskBitmap(f"/cat/black_cat000.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat001.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat002.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat003.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat004.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat005.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat006.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat007.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat008.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat009.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat010.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat011.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat012.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat013.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat014.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat015.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat016.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat017.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat018.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat019.bmp"),
    displayio.OnDiskBitmap(f"/cat/black_cat020.bmp"),
)

animation_group = displayio.Group()
animation_group.hidden = True
animation_group.scale = 1

background_bitmap = displayio.Bitmap(32, 32, 1)
background_palette = displayio.Palette(1)
background_palette[0] = 0xFFFFFF
background_sprite = displayio.TileGrid(background_bitmap, pixel_shader=background_palette, x=0, y=0)
animation_group.append(background_sprite)

cat_bitmap = cat_frames[0]
cat_palette = displayio.Palette(2)
cat_palette[0] = 0x000000
cat_palette[1] = 0xFFFFFF
cat_sprite = displayio.TileGrid(cat_bitmap, pixel_shader=cat_palette, x=0, y=0)
animation_group.append(cat_sprite)

root_group.append(animation_group)

def animate(frames, speed, backwards):
    global previous_frame
    idx = frames[0]
    if backwards:
        idx = frames[1]
    forward = not backwards
    while idx <= frames[1] and idx >= frames[0]:
        #cat_sprite.x = cat_sprite.x + speed
        animation_group.x = animation_group.x + speed
        cat_sprite.bitmap = cat_frames[idx]
        if forward:
            idx = idx + 1
        else:
            idx = idx - 1
        frame_time = time.monotonic() - previous_frame
        #while frame_time < 0.040:
        while frame_time < 0.1:
            time.sleep(0.001)
            frame_time = time.monotonic() - previous_frame
        print(frame_time)
        previous_frame = time.monotonic()

def game():
    global menu_group
    global animation_group
    menu_group.hidden = True
    animation_group.hidden = False
    prev_pos = encoder.position
    cat_speed = 0
    laps = 0
    animation_group.scale = 1
    animation_group.x = 0
    animation_group.y = 40
    while True:
        if laps == 1 and animation_group.x > 0:
            cat_speed = 0
            animate(sit_frames, cat_speed, False)
            animate(lay_frames, cat_speed, False)
            animate(sleep_frames, cat_speed, False)
            animate(sleep_frames, cat_speed, True)
            animate(lay_frames, cat_speed, True)
            animate(sit_frames, cat_speed, True)
            laps = 0
        else:
            cat_speed = 1
            if animation_group.x > 128:
                animation_group.x = -16
                laps += 1
            animate(run_frames, cat_speed, False)
            animate(run_frames, cat_speed, True)
    animation_group.hidden = True
    menu_group.hidden = False

last_time = time.monotonic()
previous_value = encoder.position
while True:
    if encoder.position > previous_value:
        last_time = time.monotonic()
        if not is_awake:
            is_awake = True
            wake()
        else:
            selection_index = next_option
    elif encoder.position < previous_value:
        last_time = time.monotonic()
        if not is_awake:
            is_awake = True
            wake()
        else:
            selection_index = prev_option
    previous_value = encoder.position

    prev_option = selection_index - 1
    if prev_option < 0:
        prev_option = len(options) - 1

    next_option = selection_index + 1
    if next_option > len(options) - 1:
        next_option = 0

    previous_label.text = f"{prev_option}:{options[prev_option]}"
    selected_label.text = f"{selection_index}:{options[selection_index]}"
    next_label.text = f"{next_option}:{options[next_option]}"

    if not button.value:
        last_time = time.monotonic()
        if not is_awake:
            is_awake = True
            wake()
        elif options[selection_index] == "Game":
            game()
        else:
            is_awake = False
            sleep()
        time.sleep(0.15)

    if options[selection_index] == "Jiggle":
        valueX = random.randint(-1, 1)
        valueY = random.randint(-1, 1)
        m.move(valueX, valueY, 0)
    elif options[selection_index] == "Click":
        m.click(Mouse.LEFT_BUTTON)
    elif options[selection_index] == "Jump":
        kbd.send(Keycode.SPACE)
    elif options[selection_index] == "Walk":
        kbd.send(Keycode.W)

    if is_awake and time.monotonic() - last_time > 10:
        is_awake = False
        sleep()

    time.sleep(0.1)
