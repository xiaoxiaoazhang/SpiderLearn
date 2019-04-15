# -*- coding=utf-8 -*-

import urllib
import urllib.request
import os
import time
import logging
# 文件压缩
from unrar import rarfile
import zipfile
# html文件解析
from bs4 import BeautifulSoup
# 正则表达式
import re
# 线程
import _thread


# 网站地址
BASE_URL = "https://m.txt2019.com"
# 下载文件保存目录
BASE_OUT_PUT_DIR = "download/txt2019"


# 爬虫抓取网页函数
def get_html(url, basedir=BASE_OUT_PUT_DIR, encoding="UTF-8"):
    html = ""
    try:
        html = urllib.request.urlopen(url, timeout=60).read()
        html = html.decode(encoding)
    except Exception as e:
        print(e)
        error_txt = "%s/error.txt" % basedir
        with open(error_txt, "a") as file:
            file.write(url + "\n")
    return html


def get_menu_urls(url):
    urls = []
    html = get_html(url)
    if html == "":
        return urls
    soup = BeautifulSoup(html, "html.parser")
    menu = soup.find("div", attrs={"class": "menu"})
    address = menu.find_all('a')
    for index in address:
        try:
            href = index.attrs["href"]
            print("name: %s, href: %s" % (index.text, href))
            if "/" == href:
                continue
            urls.append(href)
        except:
            continue
    return urls


def get_wenxue_urls(basedir, url):
    html = get_html(url, basedir)
    if html == "":
        return
    soup = BeautifulSoup(html, "html.parser")
    div_main = soup.find("div", attrs={"class": "main"})
    p_tit2 = div_main.find_all('p', attrs={"class": "tit2"})
    for index in p_tit2:
        try:
            address = index.find("a")
            href = address.attrs["href"]
            print("name: %s, href: %s" % (address.text, href))
            folder = basedir + "/" + str(href)[8:]
            # print("folder: " + folder)
            create_dir_relative(folder)
            get_item_url(folder, BASE_URL + href)
        except Exception as e:
            print(e)


def get_item_url(basedir, url):
    with open(BASE_OUT_PUT_DIR + "/index.txt", "a", encoding="utf-8") as f:
        f.write(basedir + "\n")
        print(basedir)
    html = get_html(url, basedir)
    if html == "":
        return
    soup = BeautifulSoup(html, "html.parser")
    allpage = soup.find("a", attrs={"name": "allpage", "class": "allpage"})
    if allpage is not None:
        text = allpage.text
        indexs = str(text).split("/")
        if len(indexs) > 1:
            start = indexs[0]
            end = indexs[1]
            print("start: " + start + " " + end)
            fail_txt = "%s/fail.txt" % basedir
            if (os.path.exists(fail_txt)) and (os.path.isfile(fail_txt)):
                with open(fail_txt, "r") as f:
                    for line in f.readlines():
                        if not line:
                            break
                        start = line
            for num in range(int(start), int(end) + 1):
                with open(fail_txt, "w") as file:
                    file.write(str(num))
                if num == 1:
                    page_url = "%sindex.html" % url
                else:
                    page_url = "%sindex_%d.html" % (url, num)
                print("page_url: " + page_url)
                get_current_page_url(basedir, page_url)


def get_current_page_url(basedir, url):
    html = get_html(url, basedir)
    if html == "":
        return
    soup = BeautifulSoup(html, "html.parser")
    div_main = soup.find("div", attrs={"class": "main"})
    li_bookname = div_main.find_all("li", attrs={"class": "bookname"})
    for bookname in  li_bookname:
        address = bookname.find("a")
        if address is not None:
            href = address.attrs["href"]
            print("name: %s, href: %s" % (address.text, href))
            get_book_download_url(address.text, basedir, BASE_URL + href)
        else:
            print("li_bookname doesn't have attr address!")


def get_book_download_url(title, basedir, url):
    html = get_html(url, basedir)
    if html == "":
        return
    soup = BeautifulSoup(html, "html.parser")
    div_main = soup.find("div", attrs={"class": "main"})
    book_info = div_main.find_all("a", attrs={"class": "downrar"})
    address = None
    if len(book_info) > 0:
        address = book_info[0]
    else:
        book_info = div_main.find_all("a", attrs={"class": "downtxt"})
        if len(book_info) > 0:
            address = book_info[0]

    if address is not None:
        href = address.attrs["href"]
        # print("name: %s, href: %s" % (address.text, href))
        get_download_book_url(title, basedir, BASE_URL + href)
    else:
        print("%s doesn't have address label" % url)


def get_download_book_url(title, basedir, url):
    html = get_html(url, basedir)
    if html == "":
        return
    soup = BeautifulSoup(html, "html.parser")
    div_main = soup.find("div", attrs={"class": "main"})
    if div_main is None:
        return
    td = div_main.find("td", attrs={"height": "32", "align": "center"})
    if td is None:
        return
    address = td.find("a")
    if address is None:
        return
    href = address.attrs["href"]
    save_url(title, basedir, "https://www.txt2019.com/e/DownSys" + str(href).replace("..", ""))


def save_url(title, basedir, url):
    print("downloadUrl: %s--%s--%s" % (title, basedir, url))
    with open("%s/index.txt" % basedir, "a", encoding="utf-8") as file:
        file.write(title + "|" + url + "\n")


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


# 创建目录
def create_dir(path, *paths):
    if not (os.path.exists(path)) or not (os.path.isdir(path)):
        os.mkdir(path)
    for item in paths:
        if "" == item:
            continue
        path = os.path.join(path, item)
        if not(os.path.exists(path)) or not(os.path.isdir(path)):
            os.mkdir(path)
    return path


def un_zip(file_name, folder):
    if not zipfile.is_zipfile(file_name):
        pass
    if not(os.path.exists(folder)) or not(os.path.isdir(folder)):
        os.mkdir(folder)
    zip_file = zipfile.ZipFile(file_name)
    for names in zip_file.namelist():
        zip_file.extract(names, folder)
    zip_file.close()
    print("%s unzip ok" % file_name)
    # os.remove(file_name)
    # print("%s delete ok" % file_name)


def un_rar(file_name, folder):
    if not (os.path.exists(folder)) or not (os.path.isdir(folder)):
        os.mkdir(folder)
    try:
        rar = rarfile.RarFile(file_name)
        # os.chdir(folder)
        rar.extractall(folder)
        # rar.close()
        print("%s unrar ok" % file_name)
        # os.remove(file_name)
        # print("%s delete ok" % file_name)
    except Exception as e:
        print(e)


# 获取所有rar、zip文件
def get_file_list(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path) and (file_path.endswith('.rar') or file_path.endswith('.zip')):
            list_name.append(file_path)


def rarFile(path):
    fileList = []
    get_file_list(path, fileList)
    for filePath in fileList:
        print("file: %s" % filePath)
        if str(filePath).endswith(".zip"):
            un_zip(filePath, path)
        elif str(filePath).endswith(".rar"):
            un_rar(filePath, path)


# 从网络下载地址中获取文件名
def download_file(title, url, basedir):
    try:
        r = urllib.request.urlopen(url)
        if 'Content-Disposition' in r.info():
            fileName = r.info()['Content-Disposition'].split('filename=')[1]
            fileName = fileName.replace('"', '').replace("'", "")
        elif r.url != url:
            # if we were redirected, the real file name we take from the final URL
            from os.path import basename
            from urllib.parse import urlparse
            fileName = basename(urlparse(r.url)[2])
        else:
            fileName = os.path.basename(url)
        with open("%s/index_url.txt" % basedir, "a", encoding="utf-8") as file:
            file.write(title + "|" + r.url + "\n")
        data = r.read()
        create_dir_relative("%s/file/" % basedir)
        if fileName.lower().endswith(".txt"):
            fileName = title + ".txt"
        elif fileName.lower().endswith(".rar"):
            fileName = title + ".rar"
        elif fileName.lower().endswith(".zip"):
            fileName = title + ".zip"
        with open("%s/file/%s" % (basedir, filter_invalid_window_file_name(fileName)), "wb") as file:
            file.write(data)
    except (urllib.error.HTTPError, IOError) as err:
        print(err)


# 读取文本文件
def read_file(filename, encode='UTF-8'):
    start_time = time.time()
    url_list = []
    with open(filename, 'r', encoding=encode) as f:
        for line in f:
            if not line:
                break
            url_list.append(line)

    end_time = time.time()
    print("读取文件时间花费%.2f秒" % (end_time - start_time))
    return url_list


def filter_invalid_window_file_name(old_name):
    pattern = r'[\\/:*?"<>|\r\n]+'
    new_name = re.sub(pattern, '', old_name)  # 去掉非法字符
    return new_name


def runnable_get_url(href, lock):
    basedir = BASE_OUT_PUT_DIR + "/" + href.replace("/", "")
    create_dir_relative(basedir)
    if "/wenxue/" in href:
        get_wenxue_urls(basedir, BASE_URL + href)
    else:
        get_item_url(basedir, BASE_URL + href)
    lock.release()


def runnable_download(book, lock):
    url_list = read_file(book + "/index.txt")
    index = 0
    for url in url_list:
        url_info = url.split("|")
        download_file(url_info[0], url_info[1], book)
        logging.info('%d--download--%s--finish' % (index, url))
        index = index + 1
    basedir = "{}/file".format(book)
    # 解压文件
    rarFile(basedir)
    # 释放锁
    lock.release()


# 主函数入口
def main():
    # 获取文件下载路径并保存
    create_dir_relative(BASE_OUT_PUT_DIR)
    urls = get_menu_urls(BASE_URL)
    get_url_locks = []
    for href in urls:
        lock = _thread.allocate_lock()
        lock.acquire()
        get_url_locks.append(lock)
        _thread.start_new_thread(runnable_get_url, (href, lock))

    for i in range(len(get_url_locks)):
        while get_url_locks[i].locked():
            pass
    logging.info("ready to download files!")
    # 根据保存的地址下载文件
    books = read_file(BASE_OUT_PUT_DIR + "/index.txt")
    download_locks = []
    for book in books:
        if book == "" or book == "\n":
            continue
        book = book.strip().replace("\n", "")
        # 分配锁对象
        lock = _thread.allocate_lock()
        # 给锁对象加上锁 执行加锁方法
        lock.acquire()
        # 把加好锁的对象放进列表 一同传参
        download_locks.append(lock)
        # 创建子线程
        _thread.start_new_thread(runnable_download, (book, lock))

    for i in range(len(download_locks)):
        while download_locks[i].locked():
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
    logging.info('Start of program')
    main()
    logging.info('End of program')

