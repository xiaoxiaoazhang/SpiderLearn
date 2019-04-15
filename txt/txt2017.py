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
# 文件编码检测
import chardet


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
            # print("name: %s, href: %s" % (address.text, href))
            folder = basedir + "/" + str(href)[8:]
            # print("folder: " + folder)
            create_dir_relative(folder)
            get_item_url(folder, BASE_URL + href)
        except Exception as e:
            print(e)


def get_item_url(basedir, url):
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
            # print("name: %s, href: %s" % (address.text, href))
            get_book_download_url(basedir, BASE_URL + href)
        else:
            print("li_bookname doesn't have attr address!")


def get_book_download_url(basedir, url):
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
        get_download_book_url(basedir, BASE_URL + href)
    else:
        print("%s doesn't have address label" % url)


def get_download_book_url(basedir, url):
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
    title = address.attrs["title"]
    # print("name: %s, href: %s" % (title, href))
    save_url(basedir, "https://www.txt2019.com/e/DownSys" + str(href).replace("..", ""))


def save_url(basedir, url):
    print("downloadUrl: %s--%s" % (basedir, url))
    with open("%s/index.txt" % basedir, "a") as file:
        file.write(url+"\n")


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
    os.remove(file_name)
    print("%s delete ok" % file_name)


def un_rar(file_name, folder):
    if not (os.path.exists(folder)) or not (os.path.isdir(folder)):
        os.mkdir(folder)
    try:
        rar = rarfile.RarFile(file_name)
        # os.chdir(folder)
        rar.extractall(folder)
        # rar.close()
        print("%s unrar ok" % file_name)
        os.remove(file_name)
        print("%s delete ok" % file_name)
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
def download_file(url, basedir):
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
        with open("%s/index_url.txt" % basedir, "a") as file:
            file.write(r.url + "\n")
        data = r.read()
        create_dir_relative("%s/file/" % basedir)
        with open("%s/file/%s" % (basedir, fileName), "wb") as file:
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


def get_encoding(file):
    with open(file, 'rb') as f:
        # 取1024个字节检测，如果全检测的话太耗时间
        byte_array = min(1024, os.path.getsize(file))
        return chardet.detect(f.read(byte_array))['encoding']


def filter_invalid_window_file_name(old_name):
    pattern = r'[\\/:*?"<>|\r\n]+'
    new_name = re.sub(pattern, '', old_name)  # 去掉非法字符
    return new_name


def get_file_name_from_file(file_path):
    file_name = ""
    coding = get_encoding(file_path)
    if coding is None:
        coding = "GB2312"
    print(file_path + ": " + coding)
    # 二进制格式读取文件不能设置coding
    with open(file_path, 'rb') as f:
        line_index = 10
        while line_index > 0:
            line_index -= 1
            line = f.readline()
            if not line:
                break
            try:
                line = line.decode(coding)
                pattern = re.compile(r"《.+?》|<.+?>")
                results = pattern.finditer(line)
                for result in results:
                    file_name = result.group()
                    if '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">' in file_name:
                        continue
                    file_name = file_name.replace("<", "《").replace(">", "》")
                    print(file_name)
                    file_name = filter_invalid_window_file_name(file_name)
                    line_index = 0
                    break
            except Exception as e:
                print(str(line))
                logging.error(e)
                line_index = 0
    return file_name


# 检测新文件名是否存在，若存在则改名为xxx.1.txt，若还存在则数字加一直到不存在相同为止
def check_file_name(folder, name, index=0):
    if 0 == index:
        file = os.path.join(folder, name)
    else:
        file = os.path.join(folder, "%s.%d" % (name, index))
    if os.path.exists(file) and os.path.isfile(file):
        return check_file_name(folder, name, index + 1)
    else:
        return file


def rename_file(basedir):
    for file in os.listdir(basedir):
        file_path = os.path.join(basedir, file)
        if os.path.isdir(file_path):
            rename_file(file_path)
        else:
            if file_path.endswith('.txt') and os.path.getsize(file_path) > 0 and not (file.startswith("<") or file.startswith("《")):
                new_name = get_file_name_from_file(file_path)
                if new_name != "" and file != new_name:
                    new_file = check_file_name(basedir, new_name)
                    os.rename(file_path, new_file)


# 主函数入口
def main():
    # 获取文件下载路径并保存
    create_dir_relative(BASE_OUT_PUT_DIR)
    urls = get_menu_urls(BASE_URL)
    for href in urls:
        basedir = BASE_OUT_PUT_DIR + "/" + href.replace("/", "")
        create_dir_relative(basedir)
        if "/wenxue/" in href:
            get_wenxue_urls(basedir, BASE_URL + href)
        else:
            get_item_url(basedir, BASE_URL + href)

    # 根据保存的地址下载文件
    books = ["/wenxue/gc", "/wenxue/dangdai", "/wenxue/yqxs"]
    for book in books:
        basedir = BASE_OUT_PUT_DIR + "%s" % book
        url_list = read_file(basedir + "/index.txt")
        index = 0
        for url in url_list:
            download_file(url, basedir)
            logging.info('%d--download--%s--finish' % (index, url))
            index = index + 1
        basedir = BASE_OUT_PUT_DIR + "{}/file".format(book)
        # 解压文件
        rarFile(basedir)
        # 重命名文件，这里其实可以不用，获取下载链接的时候就应该保存文件名，这个留给后面去实现
        rename_file(basedir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
    logging.info('Start of program')
    main()
    logging.info('End of program')

