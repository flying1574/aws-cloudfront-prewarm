import json
import re
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.error

def cf_code():
    url = 'https://www.feitsui.com/zh-hans/article/3'
    try:
        response = urllib.request.urlopen(url)
        html_content = response.read().decode()
        Cloudfront_Pops = re.findall(r'<td>([A-Z0-9\-]+)</td>', html_content)
    except Exception as e:
        print(f"Error occurred in cf_code: {e}")
        Cloudfront_Pops = []
    return Cloudfront_Pops

def warm(Pop, cf_id, cf_url, file_name):
    try:
        file_url = 'http://' + cf_id + '.' + Pop + '.cloudfront.net' + file_name
        header = {'Host': cf_url}
        req = urllib.request.Request(url=file_url, headers=header)
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print('FAILED: ' + 'POP:' + Pop + ' FILE:' + file_url + ' REASON:' + 'HTTPError: {}'.format(e.code))
    except urllib.error.URLError as e:
        print('FAILED: ' + 'POP:' + Pop + ' FILE:' + file_url + ' REASON:' + 'URLError: {}'.format(e.reason))
    except Exception as e:
        print('FAILED: ' + 'POP:' + Pop + ' FILE:' + file_url + ' REASON:' + str(e))
    else:
        print('SUCCESS: ' + ' POP:' + Pop + ' FILE:' + file_url)

def lambda_handler(event, context):
    Cloudfront_Url = json.loads(json.dumps(event))['cloudfront_url']
    Distributions_Id = Cloudfront_Url.split('.')[0]
    File_Name = json.loads(json.dumps(event))['filename']

    # 替换 Cloudfront_Pops 的定义
    Cloudfront_Pops = cf_code()

    # 设置线程池的大小为 Cloudfront_Pops 列表的长度
    with ThreadPoolExecutor(len(Cloudfront_Pops)) as executor:
        for Pop in Cloudfront_Pops:
            try:
                task = executor.submit(warm, Pop, Distributions_Id, Cloudfront_Url, File_Name)
            except Exception as e:
                print(e)

