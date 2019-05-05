import urllib
import urllib.request
import requests
import os
import gzip
import io
import time
import logging
# 文件压缩
# from unrar import rarfile
# import zipfile
# # html文件解析
from bs4 import BeautifulSoup
# 正则表达式
import re
# 文件编码检测
import chardet
# 线程
import _thread

BASE_URL = "https://www.80txt.com"
BASE_OUT_PUT_DIR = "80txt"


# 爬虫抓取网页函数
def get_html(url, basedir=BASE_OUT_PUT_DIR, encoding="UTF-8"):
    html = ""
    try:
        # html = urllib.request.urlopen(url, timeout=60).read()
        # html = html.decode(encoding)
        # print("getHtml: " + url)
        html = requests.get(url).content
    except Exception as e:
        print(e)
        error_txt = "%s/error.txt" % basedir
        with open(error_txt, "a") as file:
            file.write(url + "\n")
    return html


# 解压缩网页，有问题要修改
# def get_zip_html(url):
#     data = urllib.request.urlopen(url, timeout=60).read()
#     encoding = chardet.detect(data)['encoding']
#     print("encoding: " + encoding)
#     data = str(data, encoding=encoding)
#     data = io.StringIO(data)
#     gzipper = gzip.GzipFile(fileobj=data)
#     html = gzipper.read()
#     print(html)
#     soup = BeautifulSoup(html, "html.parser", fromEncoding='gb18030')
#     print(soup)
#     return html


def get_menu_urls(url, filename):
    # soup = BeautifulSoup(requests.get(url).content, "html.parser", from_encoding="utf-8")
    # soup = BeautifulSoup(requests.get(url).content, "html5lib", from_encoding="utf-8")
    soup = BeautifulSoup(requests.get(url).content, "lxml", from_encoding="utf-8")
    # print(soup.encode("gb18030"))
    # print(soup.prettify().encode(soup.original_encoding))
    # print(soup.prettify())
    menu = soup.find("div", attrs={"id": "menu"})
    # print(menu)
    address = menu.find_all('a')
    count = 0
    for index in address:
        try:
            count += 1
            href = index.attrs["href"]
            # print("name: %s, href: %s" % (index.text, href))
            with open(filename, "a", encoding="utf-8") as file:
                file.write(str(count) + "|" + index.text + "|" + BASE_URL + href + "\n")
        except:
            continue


def create_dir(folder):
    if not(os.path.exists(folder)) or not(os.path.isdir(folder)):
        os.mkdir(folder)


def get_item_url(url, basedir):
    html = get_html(url, basedir)
    # print(html)
    if html == "":
        return
    # soup = BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
    pagelink = soup.find("div", attrs={"class": "pagelink"})
    # print(pagelink)
    if pagelink is not None:
        first = pagelink.find("a", attrs={"class": "first"})
        print(first)
        start = first.text
        last = pagelink.find("a", attrs={"class": "last"})
        print(last)
        end = last.text
        print("start: " + start + " " + end)
        fail_txt = "%s/fail.txt" % basedir
        if (os.path.exists(fail_txt)) and (os.path.isfile(fail_txt)):
            with open(fail_txt, "r") as f:
                for line in f.readlines():
                    if not line:
                        break
                    start = line.split("|")[2]
        index = url.index('/1.html')
        base_url = url[0:index]
        print(base_url)
        for num in range(int(start), int(end) + 1):
            with open(fail_txt, "w", encoding="utf-8") as file:
                file.write(first.text + "|" + last.text + "|" + str(num))
            page_url = "%s/%d.html" % (base_url, num)
            print("page_url: " + page_url)
            get_current_page_url(page_url, basedir)


def get_current_page_url(url, basedir):
    html = get_html(url, basedir)
    if html == "":
        return
    # soup = BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
    div_main = soup.find("div", attrs={"class": "main"})
    div_book = div_main.find_all("div", attrs={"id": "list_art_2013"})
    # print(div_book)
    for bookitem in div_book:
        div_address = bookitem.find("div", attrs={"class": "book_bg"})
        if div_address is not None:
            address = div_address.find("a")
            href = address.attrs["href"]
            title = address.text
            print("name: %s, href: %s" % (title, href))
            get_book_download_url(title, basedir, href)
        else:
            print("div_address doesn't exist!")


def get_book_download_url(title, basedir, url):
    html = get_html(url, basedir)
    if html == "":
        return
    # soup = BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
    div_main = soup.find("div", attrs={"class": "main"})
    down_url_list = []
    # 获取公告里的txt下载链接
    main_content_div = div_main.find_all("div", attrs={"id": "main_content_2013"})
    if main_content_div is not None and len(main_content_div) > 2:
        download_div = main_content_div[2].find("div", attrs={"class": "usercom"})
        # print(download_div)
        if download_div is not None:
            address = download_div.find("a")
            href = address.attrs["href"]
            print("name: %s, href: %s" % (address.text, href))
            down_url_list.append(href)
    # 获取down.html里的下载链接
    down_url = url.replace(".html", "/down.html")
    print("down_url: " + down_url)
    html = get_html(down_url, basedir)
    if html:
        soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
        down_url_div = soup.find("div", attrs={"class": "down_url_txt"})
        if down_url_div is not None:
            address_list = down_url_div.find_all("a")
            for address_item in address_list:
                href = address_item.attrs["href"]
                title = address_item.attrs["title"]
                print("title: %s, href: %s" % (title, href))
                down_url_list.append(href)
    save_url(title, basedir, down_url_list)


def save_url(title, basedir, url_list):
    with open("%s/index.txt" % basedir, "a", encoding="utf-8") as file:
        file.write(title)
        for line in url_list:
            file.write("|" + line)
        file.write("\n")


# 读取文本文件
def read_file(filename, encode='UTF-8'):
    start_time = time.time()
    url_list = []
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, 'r', encoding=encode) as f:
            for line in f:
                if not line:
                    break
                url_list.append(line)
    end_time = time.time()
    print("读取文件时间花费%.2f秒" % (end_time - start_time))
    return url_list


# 获取当前目录下的文件夹
def get_dirs(path):
    dirs = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            dirs.append(file)
    return dirs


# 从网络下载地址中获取文件名
def download_file(url, basedir):
    try:
        res = requests.get(url, stream=True)
        # print(res.status_code == requests.codes.ok)
        # res.raise_for_status()
        create_dir("%s/file/" % basedir)
        file_name = url[url.rindex("/")+1:]
        with open("%s/file/%s" % (basedir, file_name), "wb") as file:
            # chunk是指定每次写入的大小，每次只写了512byte
            for chunk in res.iter_content(chunk_size=512):
                if chunk:
                    file.write(chunk)
        with open("%s/index_url.txt" % basedir, "a", encoding="utf-8") as file:
            file.write(url + "\n")
    except Exception as err:
        print(err)


def runnable_get_url(url, basedir, lock):
    get_item_url(url, basedir)
    lock.release()


def runnable_download(book, lock):
    basedir = BASE_OUT_PUT_DIR + "/%s" % book
    url_list = read_file(basedir + "/index.txt")
    index = 0
    for line in url_list:
        line_info = line.split("|")
        # print(line_info)
        if len(line_info) > 1:
            url = line_info[1]
            download_file(url, basedir)
            logging.info('%d--download--%s--finish' % (index, url))
            index = index + 1
    # 释放锁 传进来的锁，让他解锁
    lock.release()


# 主函数入口
def main():
    # 获取文件下载路径并保存
    create_dir(BASE_OUT_PUT_DIR)
    filename = "%s/menu.txt" % BASE_OUT_PUT_DIR
    if not os.path.exists(filename) or not os.path.isfile(filename):
        get_menu_urls(BASE_URL, filename)
    get_url_locks = []
    logging.info("ready to get urls!")
    with open(filename, "r", encoding="utf-8") as rf:
        for line in rf.readlines():
            if not line:
                break
            line = line.replace("\n", "")
            print(line)
            url_info = line.split("|")
            if len(url_info) < 3:
                continue
            basedir = BASE_OUT_PUT_DIR + "/" + url_info[1]
            create_dir(basedir)
            lock = _thread.allocate_lock()
            lock.acquire()
            get_url_locks.append(lock)
            href = url_info[2]
            _thread.start_new_thread(runnable_get_url, (href, basedir, lock))

    for i in range(len(get_url_locks)):
        logging.info("check %d thread" % i)
        while get_url_locks[i].locked():
            pass
    logging.debug("ready to download files!")
    # 根据保存的地址下载文件
    books = get_dirs(BASE_OUT_PUT_DIR)
    download_locks = []
    for book in books:
        # 分配锁对象
        lock = _thread.allocate_lock()
        # 给锁对象加上锁 执行加锁方法
        lock.acquire()
        # 把加好锁的对象放进列表 一同传参
        download_locks.append(lock)
        # 创建子线程
        _thread.start_new_thread(runnable_download, (book, lock))

    for i in range(len(books)):
        while download_locks[i].locked():
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
    logging.info('Start of program')
    main()
    logging.info('End of program')