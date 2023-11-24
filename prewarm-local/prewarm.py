#encoding:utf-8
# -*- coding: utf-8 -*-

import sys
import socket
from concurrent.futures import ThreadPoolExecutor
import http.client
import csv
import importlib
import os
import urllib.request
import re
print("Note: if you don't have domain,just put the cloudfront link!!!")
print("Note: if you don't have domain,just put the cloudfront link!!!")
print("Note: if you don't have domain,just put the cloudfront link!!!")
domain = input('Please input your domain name:')
cdn_name = input('Please input your cdn link:')
importlib.reload(sys)

file_context = open("file.txt").read().splitlines()
#domain = "xxx.cloudfront.net"  # 您的实际的自定义域名, 如果您有CNAME,则填写您的实际CNAME(xxx.example.com)，如无，则domain是xxx.cloudfront.net
#cdn_name = 'xxx.cloudfront.net'
result_file = "result.csv"
no_ip_file = "no_ip_file.csv"
cache_index = 0

def saveStringToCsv(inputString, file_path):
    out = open(file_path, 'a', encoding="utf-8", newline='')
    csv_write = csv.writer(out, dialect='excel')
    csv_write.writerow(inputString)

def cf_code():
    url = 'https://www.feitsui.com/zh-hans/article/3'
    try:
        response = urllib.request.urlopen(url)
        html_content = response.read().decode()
        Cloudfront_Pops = re.findall(r'<td>([A-Z0-9\-]+)</td>', html_content)
    except Exception as e:
        print(f"Error occurred: {e}")
        Cloudfront_Pops = []
    return Cloudfront_Pops

def CdnWarm(ip, url, dn, pop, thread_count):
    global cache_index
    try:
        conn = http.client.HTTPConnection(ip)
        conn.request(method="GET",
                     url=url,
                     headers={'Host': dn,
                              "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, lik e Gecko) Chrome/33.0.1750.152 Safari/537.36",
                              "Referer": "im is test"})
        response = conn.getresponse()
        data1 = response.read()
        f1 = open("test.jpg", "wb")
        f1.write(data1)
        f1.close()
        headers = response.getheaders()

        conn.close()

        if os.path.exists("test.jpg"):
            os.remove("test.jpg")
        else:
            print("The file does not exist")

        if cache_index == 0:
            while str(headers[cache_index]).find("from cloudfront") < 0:
                cache_index = cache_index + 1

        result = [thread_count, pop, cdn_name % (pop), url, response.status, response.getheaders()[cache_index]]
        saveStringToCsv(result, result_file)
        print(result)
        if (response.getheaders()[cache_index]) == 'Miss from cloudfront':
            CdnWarm(ip, url, dn, pop, thread_count)

    except BaseException as e:
        print(" ====================================")
        print(f"|| Thread {thread_count} {ip} error ||")
        print(e)
        print(" ====================================")
        result = [thread_count, pop, cdn_name % (pop), url, e]
        saveStringToCsv(result, result_file)

def getCdnIP(url):
    try:
        return socket.gethostbyname(url)
    except Exception as e:
        return 0

def CdnThreadFunc():
    global cdn_name
    cdnUrls = cdn_name.split(".")
    cdn_name = cdnUrls[0] + ".%s." + cdnUrls[1] + "." + cdnUrls[2]

    Cloudfront_Pops = cf_code()

    # 设置线程池的大小为 CDN 节点数量
    thread_pool_size = len(Cloudfront_Pops)

    with ThreadPoolExecutor(thread_pool_size) as executor:
        thread_count = 0  # 用于标记线程编号
        for pop in Cloudfront_Pops:
            low_pop = pop.lower()
            new_cdn = cdn_name % (low_pop)
            ip = getCdnIP(new_cdn)
            if ip == 0:
                list = [thread_count, pop, new_cdn, "无法解析该pop点"]
                saveStringToCsv(list, no_ip_file)
                print(list)
            for url in file_context:
                low_pop = pop.lower()
                new_url = url.replace("http://", "")
                new_url = new_url.replace("https://", "")
                new_url = new_url.replace(domain, "")
                task = executor.submit(CdnWarm, new_cdn, new_url, domain, low_pop, thread_count)
                thread_count += 1

CdnThreadFunc()

