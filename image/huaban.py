# -*- coding=utf-8 -*-

import re
import os
import requests
import time
import logging
import constants

# 保存文件目录，当前目录download下
OUT_PUT_DIR = 'huaban'
# 请求头
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
# 下载地址
BASE_URL = "http://huaban.com/favorite/beauty/"
DOWNLOAD_URL = "http://hbimg.b0.upaiyun.com/"
NEXT_URL = "http://huaban.com/favorite/beauty/?iqkxaeyv&limit=20&wfl=1&max="


# 图片下载
def down(file, url):
    try:
        r = requests.get(url, stream=True)
        with open(file, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
    except Exception as e:
        print(e)


# 获取图片分类
def get_items(url):
    try:
        page = requests.session().get(url, headers=HEAD, timeout=60)
        page.encoding = "utf-8"
        return page.text
    except Exception as e:
        print(e)
        time.sleep(5)
        get_items(url)


# 获取当前页图片url
def get_url(url, outdir):
    text = get_items(url)
    pattern = re.compile('{"pin_id":(\d*?),.*?"key":"(.*?)",.*?"like_count":(\d*?),.*?"repin_count":(\d*?),.*?}', re.S)
    items = re.findall(pattern, text)
    print(items)
    max_pin_id = 0
    for item in items:
        max_pin_id = item[0]
        x_key = item[1]
        x_like_count = int(item[2])
        x_repin_count = int(item[3])
        if (x_repin_count > 10 and x_like_count > 10) or x_repin_count > 100 or x_like_count > 20:
            url_item = DOWNLOAD_URL + x_key
            filename = "%s/%s.jpg" % (outdir, str(max_pin_id))
            if is_file_exist(filename):
                continue
            down(filename, url_item)
    get_url(NEXT_URL + max_pin_id, outdir)


# 创建目录
def create_dir_relative(path):
    paths = path.split(os.altsep)
    path = os.getcwd()
    for item in paths:
        if item == "":
            continue
        path = os.path.join(path, item)
        logging.debug(path)
        if not(os.path.exists(path)) or not(os.path.isdir(path)):
            os.mkdir(path)
    return path


# 创建保存目录
def create_dir(path, *paths):
    if not (os.path.exists(path)) or not (os.path.isdir(path)):
        os.mkdir(path)
    for item in paths:
        path = os.path.join(path, item)
        logging.debug(path)
        if not(os.path.exists(path)) or not(os.path.isdir(path)):
            os.mkdir(path)
    return path


def is_file_exist(path):
    if os.path.exists(path) and os.path.isfile(path):
        return True
    return False


def main():
    outdir = create_dir(constants.CUR_DIR, constants.DOWNLOAD_DIR, OUT_PUT_DIR)
    get_url(BASE_URL, outdir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
    logging.info('Start of program')
    main()
    logging.info('End of program')
