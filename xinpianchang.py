import json
import linecache
import os
import random
import re

import requests
import pymysql

from bs4 import BeautifulSoup

def download_page(url):
    header = get_header()
    print(header)
    html = requests.get(url, header)
    return html.text

def get_header():
    with open("header.txt", "r", encoding="utf-8") as file:
        headers = file.read()
    n = headers.count('\n')
    i = random.randint(1, (n+1))
    header = linecache.getline(r'header.txt', i)
    return header
    file = open("header.txt", "r", encoding="utf-8")
    header = file.readline()
    while header != '':
        header = file.readline()
        # print(header)
        yield header

def get_content(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    con = soup.find(class_ = 'video-list')
    if_next = soup.find('div', class_ = 'page').find_all('a')[-1]
    if if_next['href'] and if_next['title'] and if_next['title'] == '下一页' and if_next['href'] != url:
        next_url = if_next['href']
    else:
        next_url = ''
    con_list = con.find_all('li', class_='enter-filmplay')
    for i in con_list:
        article_id = i['data-articleid']
        photo_url = i.find('img', class_ = 'lazy-img')['_src']
        duration = i.find('span', class_ = 'duration fs_12').get_text()
        title = i.find('p', class_ = 'line-hide-1').get_text()
        play_volume = i.find('span', class_ = 'icon-play-volume').get_text()
        like_volume = i.find('span', class_ = 'icon-like').get_text()
        types = i.find('div', class_ = 'new-cate').find_all('span')
        type_list = [type.get_text() for type in types]
        try:
            authors = i.find('ul', class_ = 'authors-list').find_all('li')
            author_id_list = [li['data-userid'] for li in authors]
        except:
            author_id = i.find('span', class_ = 'head-wrap')['data-userid']
            author_id_list.append(author_id)
        positive_url = "https://www.xinpianchang.com/a%s?from=ArticleList" % article_id
        # positive_html = download_page(positive_url)
        positive_html = test("positive.html")
        vid = re.search(r'vid:\ "(\S*)"', positive_html, re.S).group(1)
        requireDomain = re.search(r'requireDomain:\ "([a-zA-z]+://[^\s]*)"', positive_html, re.S).group(1)
        get_qiniu_url = "%s/video/%s" % (requireDomain,vid)   # https://openapi-vtom.vmovier.com/video/5CE1641D1AC9D
        # get_qiniu_html = download_page(get_qiniu_url)
        get_qiniu_html = test('get_qiniu_html.html')
        qiniu_url = BeautifulSoup(get_qiniu_html, 'html.parser').find('video', class_='video-js')['src']
        video_id = re.search(r'com/(\w*).mp4',qiniu_url).group(1)
        video_url = "https://qiniu-xpc0.xpccdn.com/%s.mp4" % video_id   # 最后的结果
        video_bg = re.search(r"cover:\ '([a-zA-z]+://[^\s]*)'", positive_html, re.S).group(1)
        print_test(video_url)
        exit()

    return next_url
        # print_test(author_id_list)

def get_author_info(author_id_list):
    author_dict = {}
    for author_id in author_id_list:
        home_page = "https://www.xinpianchang.com/user/space/id-%d/d-1" % author_id
        # home_page_html = download_page(home_page)
        home_page_html = test('create_info.html')
        soup = BeautifulSoup(home_page_html, 'html.parser')
        bg = soup.find(class_ = 'banner-wrap')
        big_bg_url = bg['style']
        bg_img_url = (re.search(re.compile(r'(\()(.*?)(\))', re.S),big_bg_url)).group(2)
        head_portrait = bg.find('span', class_='avator-wrap-s').find('img')['src']
        color_v = bg.find('span', class_='avator-wrap-s').find('span', class_='author-v')['class'][1]
        creator_info = soup.find('div', class_='creator-info')
        ps = creator_info.find_all('p')
        creator_name = ps[0].get_text()
        creator_desc = ps[1].get_text()
        creator_detail = ps[2].find_all('span', recursive=False)    # recursive 只对直属下级节点进行搜索 不检查子孙节点
        like_counts = creator_detail[0].find('span', class_='like-counts').get_text()
        like_counts = int("".join(like_counts.split(',')))
        fans_counts = creator_detail[1].find('span', class_='fans-counts').get_text()
        fans_counts = int("".join(fans_counts.split(',')))
        follow_wrap = creator_detail[2].find_all('span')[1].get_text()
        follow_wrap = int("".join(follow_wrap.split(',')))
        city = creator_detail[4].get_text()
        professional = creator_detail[6].get_text()

def save(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def print_test(test):
    print('\n\n\n=============================\n',
          '\n-------content-------\n', test,
          '\n-------- type -------\n', type(test),
          '\n--------- len -------\n', ("int 类型, 无 len") if (isinstance(test,int)) else (len(test)),
          '\n===============================\n\n\n')

def test(filename):
    html = open(filename, 'r', encoding='utf-8').read()
    return html

def connect_db(data, table_name):
    db = pymysql.connect(host = 'localhost',
                         port = 3306,
                         user = 'root',
                         password = '123',
                         database = 'xinpianchang',
                         charset = 'utf8',
                         )
    cursor = db.cursor()
    sql = "INSORT INTO %s ('photo_url', 'duration', 'title', 'play_volume', 'like_volume', 'type_list', 'author_id_list') VALUES ('%s', '%s', '%s', '%d', '%d', ')"
    try:
        cursor.execute(sql % data)
        db.commit()
        print('成功插入 ', cursor.rowcount, ' 条数据')
    except  Exception as e:
        db.rollback()
        print('插入失败: ', e)
    cursor.close()
    db.close()




def main():
    next_url = 'aa'
    author_id_list = [10001822]
    get_author_info(author_id_list)
    while next_url != '':
        url = "https://www.xinpianchang.com/c" + next_url
        # url = "https://www.xinpianchang.com/channel/index/type-/sort-like/duration_type-0/resolution_type-/page-1"
        # html = download_page(next_url)
        html = test('xinpianchang.html')
        next_url = get_content(html,url)
        exit()
        # print(html)
        # print(type(html))

if __name__ == '__main__':
    main()

