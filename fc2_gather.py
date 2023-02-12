# -*- coding:utf-8 -*-
# 批量获取fc2 影片磁力
#name = fc2_gater
#version = 'v0.01'

import requests, os, sys, time, re, threading
from configparser import RawConfigParser
from traceback import format_exc

#读取&初始化配置文件
def read_config():
    if os.path.exists('config.ini'):
        config_settings = RawConfigParser()
        try:
            config_settings.read('config.ini', encoding='UTF-8-SIG')  # UTF-8-SIG 适配 Windows 记事本
            proxy = config_settings.get("下载设置", "Proxy")
            download_path = config_settings.get("下载设置", "Download_Path")
            max_dl = config_settings.get("下载设置", "Max_dl")
            max_retry = config_settings.get("下载设置", "Max_retry")

            # 创建文件夹
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            return (proxy,download_path,max_dl,max_retry)
        except:
            print(format_exc())
            print('× 无法读取 config.ini。如果这是旧版本的配置文件，请删除后重试。\n')
            print('按任意键退出程序...');os.system('pause>nul')
            sys.exit()
    else:
        context='''[下载设置]
# http / socks5 局部代理 
# http 代理格式为 https://adult.contents.fc2.com/:8088 , 如 http://localhost:8088 
# socks5 代理格式为 socks5://ip:端口 , 如 socks5://localhost:Proxy = 

#存储番号文件目录 
Download_path = ./Downloads/

# 下载线程数 
# 若网络不稳定、丢包率或延迟较高，可适当减小下载线程数 
# 默认线程2，小量数据不建议修改，多线程容易报502，建议线程 n/30
Max_dl = 2

# 下载失败重试数 
# 若网络不稳定、丢包率或延迟较高，可适当增加失败重试数 
# 避免晚上网络高峰期爬取大量数据，容易报错，也会增加服务器负担
Max_retry = 3'''
        txt = open("config.ini", 'a', encoding="utf-8")
        txt.write(context)
        txt.close()
        print('× 没有找到 config.ini。已生成，请修改配置后重新运行程序。\n')
        print('按任意键退出程序...');os.system('pause>nul')
        sys.exit()

def fc2_get_current_page(txt):#获当前页码
    pattern = re.compile('<span class="items" aria-selected="true">([0-9]*)</span>', re.S)
    keys = re.findall(pattern, txt)
    if not keys==[]:
        return int(keys[0])

def fc2_get_next_page(txt):#获取下一页
    pattern = re.compile('<span class="items" aria-selected="true">.*?</span>.*?<a data-pjx="pjx-container" data-link-name="pager".*?href=".*?&page=([0-9]*)" class="items">.*?<', re.S)
    keys = re.findall(pattern, txt)
    if not keys==[]:
        return int(keys[0])
    else:return 0

# 获取网页数据
def requests_web(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    try:
        if proxy == '否' or proxy =='no' or proxy =='':
            response = session.get(url, headers=headers)
        else:
            response = session.get(url, headers=headers,proxies=proxie)
        response.encoding = 'utf-8'
    except:
        print(format_exc())
        print('× 网络连接异常且重试 ' + str(max_retry) + ' 次失败')
        print('× 请尝试开启全局代理或配置 HTTP 局部代理；若已开启代理，请检查其可用性')
        return None
        sys.exit()

    if response.status_code != 200:
        print('x 连接错误：'+str(response.status_code))
        return None
        sys.exit()
    else:
        return response.text

#获取番号正则
def parse_fc2id(txt):
    pattern = re.compile('<div class="c-cntCard-110-f"><div class="c-cntCard-110-f_thumb"><a href="/article/([0-9]*)/"', re.S)
    keys = re.findall(pattern, txt)
    for item in keys:
        yield item

#获取磁力正则
def parse_magnet(html):
    pattern = re.compile('<a href="magnet:\?xt=(.*?)&amp;dn=', re.S)
    urls = re.findall(pattern, html)
    if not urls==[]:
        return 'magnet:?xt='+urls[0]

#获取每页番号并导出txt
def get_fc2id(url):
    clean_list('list.txt')
    i=1;n=1
    while i<=n:
        html=requests_web(url)
        f2ids = parse_fc2id(html)
        for num in f2ids:
            write_to_file('list.txt', 'FC2 '+str(num))
        i=i+1
        n=fc2_get_next_page(html)
        url=url+'&page='+str(n)
    print('获取番号列表完成，数据已存到' + download_path + 'list.txt文件中')

#获取磁力链接并导出txt
def get_magnet(start,stop):
    for i in range(start,stop):
        url = 'https://sukebei.nyaa.si/?f=0&c=0_0&q=' + idlist[i]+'&s=downloads&o=desc'
        html = requests_web(url)
        if html is not None:
            magnet = parse_magnet(html)
            if magnet is not None:
                f = open(download_path + 'magnet.txt', 'a', encoding='UTF-8')
                mu.acquire()
                print('已找到磁力，数据写入magnet.txt文件中 ====> ' + idlist[i])
                f.write(str(magnet) + '\n')
                time.sleep(1)
                f.close()
                mu.release()
            else:
                f = open(download_path + 'no_magnet.txt', 'a', encoding='UTF-8')
                mu.acquire()
                print('× 没有磁力，失败列表写入no_magnet.txt ====> ' + idlist[i])
                f.write(idlist[i])
                time.sleep(1)
                f.close()
                mu.release()
        else:
            mu.acquire()
            write_to_file('error.txt',idlist[i].replace('\n','')+'--连接失败')
            time.sleep(1)
            mu.release()



#读取本地txt番号list
def read_list(file):
    file = download_path + file
    if os.path.exists(file):
        try:
            f2 = open(file, encoding='utf-8')
            line = f2.readlines()
            f2.close()
        except:
            print(format_exc())
            print('× 打开文件失败重试')
        return line
    else:
        print('× 没找到番号列表list.txt文件！请重新获取番号列表！')


#写入txt
def write_to_file(filename,txt):
    filename=download_path+filename
    print('开始写入数据 ====> ' + str(txt))
    with open(filename, 'a', encoding='UTF-8') as f:
        f.write(txt+'\n')
        f.close()
#清空输出txt文件
def clean_list(filename):
    filename = download_path + filename
    print('× 清空txt数据 ===>'+filename)
    with open(filename, 'w', encoding='UTF-8') as f:
        f.truncate(0)
        f.close()

#多线程，按线程数分组
def creta_thread():
    lmax = len(idlist)
    remaider = lmax % int(max_dl)
    number = int(lmax / int(max_dl))
    offset = 0
    for i in range(int(max_dl)):
        if remaider > 0:
            t = threading.Thread(target=get_magnet, args=(i * number + offset, (i + 1) * number + offset + 1))
            remaider = remaider - 1
            offset = offset + 1
        else:
            t = threading.Thread(target=get_magnet, args=(i * number + offset, (i + 1) * number + offset))
        t.start()
        time.sleep(0.1)

#获取用户输出url，并简单判断合规
def input_url():
    print('例如：https://adult.contents.fc2.com/users/yamasha/articles?sort=date&order=desc')
    while True:
        url = input("请输入需要抓取番号的网页：")
        fc2url='https://adult.contents.fc2.com'
        if fc2url in url:
            return url
            break
        else:
            print('× 输入有误,请输入正确的网址')
#菜单
def set_memu():
    running = True
    menu = """
     Main Menu  
--------------------
   1: 获取番号
   2: 获取磁力
   q: Quit
--------------------
"""
    global idlist
    while running:
        print(menu)
        cmd = str(input("请选择操作:"))
        if cmd != 'q':
            os.system('cls')
            try:
                #print(menu)
                if cmd != None:
                    if cmd == '1':
                        target_url=input_url()
                        get_fc2id(target_url)
                        continue
                    elif cmd == '2':
                        idlist = read_list('list.txt')
                        if idlist is not None or idlist!=[]:
                            clean_list('magnet.txt')
                            clean_list('no_magnet.txt')
                            clean_list('error.txt')
                            creta_thread()
                            while threading.active_count() != 1:
                                pass
                            else:
                                print('获取磁力完成，数据已存到' + download_path)

                        else:
                            print('× 没找到番号列表list.txt文件！请重新获取番号列表！')

                    else:
                        print('× 输入有误，清输入菜单指定字符!')
            except:
                print(menu)
        else:
            print('即将退出...')
            os.system('cls')
            sys.exit()

if __name__ == '__main__':
    (proxy, download_path, max_dl, max_retry) = read_config()
    if not proxy == '否': proxie = {'http': proxy , 'https': proxy}
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=max_retry))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=max_retry))
    target_url=''
    idlist = read_list("list.txt")
    mu = threading.Lock()
    set_memu()

