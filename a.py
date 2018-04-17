#-*-coding:utf-8-*-
import os
import sys
import subprocess
import shutil
import time
import math
from PIL import Image, ImageDraw
import random
import json
import re


# === ˼· ===
# ���ģ�ÿ������֮���ͼ�����ݽ�ͼ������ӵ��������һ���鶥����е����꣬
#      ����������ľ������һ��ʱ��ϵ����ó�����ʱ��
# ʶ�����ӣ������ӵ���ɫ��ʶ��λ�ã�ͨ����ͼ����������һ�д����һ��ֱ�ߣ��ʹ�������һ��һ�б�����
#      �Ƚ���ɫ����ɫ����һ���������Ƚϣ��ҵ����������һ�е����е㣬Ȼ������е㣬
#      ���֮������ Y �������С���ӵ��̵�һ��߶ȴӶ��õ����ĵ������
# ʶ�����̣�����ɫ�ͷ����ɫ���������ӷ���֮�µ�λ�ÿ�ʼ��һ��һ��ɨ�裬����Բ�εĿ������һ���ߣ�
#      ���ε���������һ���㣬���Ծ�������ʶ�����ӵ�������ʶ���˼��������е㣬
#      ��ʱ��õ��˿��е�� X �����꣬��ʱ��������������ڵ�ǰ������ģ�
#      ����һ��ͨ����ͼ��ȡ�Ĺ̶��ĽǶ����Ƴ��е�� Y ����
# ��󣺸��������������������ϵ������ȡ����ʱ�䣨�ƺ�����ֱ���� X ����룩


# TODO: �����λƫ�Ƶ�����
# TODO: �������������ĵ���������Ƿ���ͬ������ǵĻ���������ж�һ�µ�ǰ��ǰ������󣬱��ڽ���
# TODO: һЩ�̶�ֵ���ݽ�ͼ�ľ����С����
# TODO: ֱ���� X �������߼�


def open_accordant_config():
    screen_size = _get_screen_size()
    config_file = "{path}/config/{screen_size}/config.json".format(
        path=sys.path[0],
        screen_size=screen_size
    )
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            print("Load config file from {}".format(config_file))
            return json.load(f)
    else:
        with open('{}/config/default.json'.format(sys.path[0]), 'r') as f:
            print("Load default config")
            return json.load(f)


def _get_screen_size():
    size_str = os.popen('adb shell wm size').read()
    if not size_str:
        print('�밲װADB�����������û�������')
        sys.exit()
    m = re.search('(\d+)x(\d+)', size_str)
    if m:
        width = m.group(1)
        height = m.group(2)
        return "{height}x{width}".format(height=height, width=width)


config = open_accordant_config()

# Magic Number�������ÿ����޷�����ִ�У�����ݾ����ͼ���ϵ��°�������
under_game_score_y = config['under_game_score_y']
press_coefficient = config['press_coefficient']       # ������ʱ��ϵ�������Լ�����ʵ���������
piece_base_height_1_2 = config['piece_base_height_1_2']   # ����֮һ�����ӵ����߶ȣ�����Ҫ����
piece_body_width = config['piece_body_width']             # ���ӵĿ�ȣ��Ƚ�ͼ����������΢��һ��Ƚϰ�ȫ������Ҫ����

# ģ�ⰴѹ����ʼ�����꣬��Ҫ�Զ��ظ���Ϸ�����óɡ�����һ�֡�������
if config.get('swipe'):
    swipe = config['swipe']
else:
    swipe = {}
    #����ģ�ⰴѹ���������������̨�ֻ����ԣ�����2160x1080�����������Ϊ320��1210��720��910
    #ʹ��vivox20������ȫ������С��mix2���Թ������ɴﵽ2000+�������ǵ��ڿ��������ô�usb��ȫ��֤��
    swipe['x1'], swipe['y1'], swipe['x2'], swipe['y2'] = 320, 410, 320, 410


screenshot_way = 2
screenshot_backup_dir = 'screenshot_backups/'
if not os.path.isdir(screenshot_backup_dir):
    os.mkdir(screenshot_backup_dir)


def pull_screenshot():
    global screenshot_way
    # �µķ��������Ч�ʼ��������ɸߵ�������
    if screenshot_way == 2 or screenshot_way == 1:
        process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        screenshot = process.stdout.read()
        if screenshot_way == 2:
          binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        else:
          binary_screenshot = screenshot.replace(b'\r\r\n', b'\n')
        f = open('autojump.png', 'wb')
        f.write(binary_screenshot)
        f.close()
    elif screenshot_way == 0:
        os.system('adb shell screencap -p /sdcard/autojump.png')
        os.system('adb pull /sdcard/autojump.png .')


def backup_screenshot(ts):
    # Ϊ�˷���ʧ�ܵ�ʱ�� debug
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy('autojump.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y):
    draw = ImageDraw.Draw(im)
    # ��debugͼƬ������ϸ��ע��
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=3)
    draw.line((piece_x, 0, piece_x, im.size[1]), fill=(255, 0, 0))
    draw.line((0, piece_y, im.size[0], piece_y), fill=(255, 0, 0))
    draw.line((board_x, 0, board_x, im.size[1]), fill=(0, 0, 255))
    draw.line((0, board_y, im.size[0], board_y), fill=(0, 0, 255))
    draw.ellipse((piece_x - 10, piece_y - 10, piece_x + 10, piece_y + 10), fill=(255, 0, 0))
    draw.ellipse((board_x - 10, board_y - 10, board_x + 10, board_y + 10), fill=(0, 0, 255))
    del draw
    im.save('{}{}_d.png'.format(screenshot_backup_dir, ts))


def set_button_position(im):
    # ��swipe����Ϊ `����һ��` ��ť��λ��
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = w / 2
    top = int(1584 * (h / 1920.0))
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


def jump(distance):
    press_time = distance * press_coefficient
    press_time = max(press_time, 200)   # ���� 200 ms ����С�İ�ѹʱ��
    press_time = int(press_time)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time
    )
    print(cmd)
    os.system(cmd)
    return press_time

def find_piece_and_board(im):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # ɨ������ʱ�����ұ߽�
    scan_start_y = 0  # ɨ�����ʼy����
    im_pixel=im.load()
    # ��50px����������̽��scan_start_y
    for i in range(int(h / 3), int( h*2 /3 ), 50):
        last_pixel = im_pixel[0,i]
        for j in range(1, w):
            pixel=im_pixel[j,i]
            # ���Ǵ�ɫ���ߣ����¼scan_start_y��ֵ��׼������ѭ��
            if pixel[0] != last_pixel[0] or pixel[1] != last_pixel[1] or pixel[2] != last_pixel[2]:
                scan_start_y = i - 50
                break
        if scan_start_y:
            break
    print('scan_start_y: ', scan_start_y)

    # ��scan_start_y��ʼ����ɨ�裬����Ӧλ����Ļ�ϰ벿�֣������ݶ�������2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        for j in range(scan_x_border, w - scan_x_border):  # �����귽��Ҳ������һ����ɨ�迪��
            pixel = im_pixel[j,i]
            # �������ӵ�����е���ɫ�жϣ������һ����Щ���ƽ��ֵ�������ɫ����Ӧ�� OK����ʱ�������
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = int(piece_x_sum / piece_x_c);
    piece_y = piece_y_max - piece_base_height_1_2  # �������ӵ��̸߶ȵ�һ��

    #��������ɨ��ĺ����꣬��������bug
    if piece_x < w/2:
        board_x_start = piece_x
        board_x_end = w
    else:
        board_x_start = 0
        board_x_end = piece_x

    for i in range(int(h / 3), int(h * 2 / 3)):
        last_pixel = im_pixel[0, i]
        if board_x or board_y:
            break
        board_x_sum = 0
        board_x_c = 0

        for j in range(int(board_x_start), int(board_x_end)):
            pixel = im_pixel[j,i]
            # �޵��Դ�����һ��С���ӻ��ߵ������ bug
            if abs(j - piece_x) < piece_body_width:
                continue

            # �޵�Բ����ʱ��һ���ߵ��µ�С bug�������ɫ�ж�Ӧ�� OK����ʱ�������
            if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 10:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c
    last_pixel=im_pixel[board_x,i]

    #���϶�������+274��λ�ÿ�ʼ��������ɫ���϶���һ���ĵ㣬Ϊ�¶���
    #�÷��������д�ɫƽ��Ͳ��ַǴ�ɫƽ����Ч���Ը߶����ƺ�桢ľ�����桢ҩƿ�ͷ����εĵ����������ǣ����жϴ���
    for k in range(i+274, i, -1): #274ȡ����ʱ���ķ�������¶������
        pixel = im_pixel[board_x,k]
        if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((i+k) / 2)

    #�����һ�������м䣬���¸�Ŀ�����Ļ����r245 g245 b245�ĵ㣬������������ֲ���һ�δ�����ܴ��ڵ��жϴ���
    #����һ������ĳ��ԭ��û���������м䣬����һ��ǡ�����޷���ȷʶ���ƣ����п�����Ϸʧ�ܣ����ڻ������ͨ���Ƚϴ�ʧ�ܸ��ʽϵ�
    for l in range(i, i+200):
        pixel = im_pixel[board_x,l]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
            board_y = l+10
            break



    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, board_y

def dump_device_info():
    size_str = os.popen('adb shell wm size').read()
    device_str = os.popen('adb shell getprop ro.product.model').read()
    density_str = os.popen('adb shell wm density').read()
    print("�����Ľű��޷��������ϱ�issueʱ��copy������Ϣ:\n**********\
        \nScreen: {size}\nDensity: {dpi}\nDeviceType: {type}\nOS: {os}\nPython: {python}\n**********".format(
            size=size_str.strip(),
            type=device_str.strip(),
            dpi=density_str.strip(),
            os=sys.platform,
            python=sys.version
    ))


def check_screenshot():
    global screenshot_way
    if os.path.isfile('autojump.png'):
        os.remove('autojump.png')
    if (screenshot_way < 0):
        print('�ݲ�֧�ֵ�ǰ�豸')
        sys.exit()
    pull_screenshot()
    try:
        Image.open('./autojump.png').load()
        print('���÷�ʽ{}��ȡ��ͼ'.format(screenshot_way))
    except:
        screenshot_way -= 1
        check_screenshot()

def main():

    dump_device_info()
    check_screenshot()

    while True:
        pull_screenshot()
        im = Image.open('./autojump.png')
        # ��ȡ���Ӻ� board ��λ��
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = int(time.time())
        print(ts, piece_x, piece_y, board_x, board_y)
        set_button_position(im)
        jump(math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2))
        save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y)
        backup_screenshot(ts)
        time.sleep(1)   # Ϊ�˱�֤��ͼ��ʱ��Ӧ�����ˣ����ӳ�һ���


if __name__ == '__main__':
    main()
