#coding=utf-8
import urllib2
import random
import re
import requests
import logging
from multiprocessing import Pool
import os,time,random,threading
import sys

logging.basicConfig(filename='logger.log', level=logging.INFO)
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')

def mkdir(path):
    # 引入模块
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        #print path+' 创建成功'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print path+' 目录已存在'
        return False


def get_handurl(url):
    temp=url.split("/")
    temp.pop()
    str="/"
    url=str.join(temp)+"/"
    return url

'''
GET /1DQ1aTtf6dHJfDD99PnNTrsWEddoRdudeQ/ HTTP/1.1
Host: 127.0.0.1:43110
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
'''
def getContent(url):
    """
    此函数用于抓取返回403禁止访问的网页
    """
    headers = [" Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"]
    random_header = random.choice(headers)

    """
    对于Request中的第二个参数headers，它是字典型参数，所以在传入时
    也可以直接将个字典传入，字典中就是下面元组的键值对应
    """
    req =urllib2.Request(url)
    req.add_header("GET",url)
    req.add_header("Host","127.0.0.1:43110")
    req.add_header("User-Agent", random_header)
    req.add_header("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
    req.add_header("Accept-Encoding","gzip, deflate, br")
    req.add_header("Accept-Language","zh-CN,zh;q=0.9")
    req.add_header("GET","url")
    content=urllib2.urlopen(req).read()
    return content
    #req.add_header("Referer","http://www.csdn.net/")
def get_realcontext(url):
    p=re.compile(r'wrapper_nonce = "[0-9a-z]+"')
    context=getContent(url)
    wrapper_nonce=p.findall(context)[0].split("\"")[1]
    url2=url+"?wrapper_nonce="+wrapper_nonce
    return getContent(url2)
def get_pagelink(url): #<a href="list-2.html">2</a>
    page=re.compile(r'<a href="(list-[0-9]\.html|[0-9]\.html)">')
    context=get_realcontext(url)
    page_temp=page.findall(context)
    count=0
    page_temp.append(url.split('/')[-1])
    #page_list=page_temp   #存放每页链接的list
    page_list=list(set(page_temp))
    page_list.sort()
    return page_list
#获取每页上所有girl合集的链接
def get_onepage_girllink(url):
    #<a href="beautyleg-171117-1529/1.html">
    link=re.compile(r'<a href="[a-z\.\-0-9/]+"><img src')
    context=get_realcontext(url)
    page_temp=link.findall(context)
    #print page_temp

    page_list=[]   #存放每页链接的list
    for i in page_temp:
        page_list.append(i.split("\"")[1])
    return page_list
def save_image(imgUrl,place,name):
    kind="xiuren"#beautyleg
    fpath='{2}/{0}/{1}.jpg'.format(place,name,kind)
    while(1):
        if os.path.exists(fpath):
            fsize = os.path.getsize(fpath)
            fsize = fsize/float(1024)
            if (fsize>10):
                print "exist %s : %s"%(place,name)
                return
            else:
                os.remove(fpath)
        mkdir(path="{0}\\{2}\\{1}\\".format(os.getcwd(),place,kind))
        print "down %s : %s"%(place,name)
        with open('{0}\\{3}\\{1}\\{2}.jpg'.format(os.getcwd(),place,name,kind), 'wb') as file:
            file.write(requests.get(imgUrl).content)
    return
'''
    logging.info("start")
    for i, j in enumerate(imgUrlList):
        logging.info("start %s"%j)
        with open('E:/{0}.jpg'.format(i), 'wb') as file:
            file.write(requests.get(j).content)
            logging.info("down %s"%j)
'''

#the url is a girl's link
#<img src="https://img13.pixhost.org/images/224/52683532_1506-001.jpg" alt="">
def get_imagelink(url):
    #a="<img src=\"https://img13.pixhost.org/images/224/52683532_1506-001.jpg\" alt=\"\">"
    image=re.compile(r'<img src="[0-9a-z:/_\-\.]+?" alt="" />')
    #page_list=get_pagelink(url)
    image_list=[]
    context=get_realcontext(url)
    #print context
    temp=image.findall(context)
    #print temp
    for image in temp:
        image_list.append(image.split("\"")[1])
    """
    for link in page_list:
        context=get_realcontext(link)
        count=0
        for image in image.findall(context):
            image_list.append(image.split("\"")[xxx])
    """
    return image_list
#imgine=re.compile(r'<img[\s]+src="[0-9a-z/:._-]+" alt="" [^,]+?" />')
#<a href="beautyleg-171117-1529/1.html"><img src="https://img14.pixhost.org/images/498/57405498_beautyleg-171117-1529-cover.jpg" alt="" title="[Beautyleg-171117-1529] Nancy"></a>
#<img src="https://img14.pixhost.org/images/498/57405478_beautyleg-171106-1524-cover.jpg" alt="" title="[Beautyleg-171106-1524] Tina" /></a>
def get_cover(url):
    cover=re.compile(r'<img src="[0-9a-z-/:._]+?" alt="" title="[^,]+?" /></a>')
    #name=re.compile(r'<img src="[0-9a-z-/:._]+?" alt="" title="([^,]+?)" /></a>')
    context=get_realcontext(url)
    page_temp=cover.findall(context)
    cover_list=[]
    name_list=[]
    for i in page_temp:
        temp=i.split("\"")
        cover_list.append(temp[1])
        name_list.append(temp[5].decode('utf-8','ignore').encode('gbk'))
    #print context
    return cover_list,name_list#,name.findall(context)
def get_name(url):
    #</span>[Beautyleg-170925-1506] Emma (1/6)</a></h1>
    name=re.compile(r'</span>([^"]+?)\(1/[0-9]+?\)</a></h1>')
    return name.findall(get_realcontext(url))
def save_girl(i,url):
    i=get_handurl(url)+i
    girl_page=get_pagelink(i)
    image_list=[]
    for page in  girl_page:
        page=get_handurl(i)+page
        image_list.extend(get_imagelink(page))
    place=get_name(i)[0].rstrip().decode('utf-8','ignore').encode('gbk')
    print "start %s "%(place)
    m=0
    for imageurl in image_list:
        m=m+1
        save_image(imageurl,place,m)
    return
def test(i):
    print 'Run task %s (%s)...' %(name,os.getpid())
    start = time.time()
    time.sleep(random.random()*3)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name,(end-start))
if __name__=='__main__':
    #url="http://127.0.0.1:43110/1BLxYeHot8MioHmNyeoQUA8PLo2DJKD8KS/image/qcwm-beautyleg/list-1.html"  #beautyleg
    url2="http://127.0.0.1:43110/1BLxYeHot8MioHmNyeoQUA8PLo2DJKD8KS/image/qcwm-beautyleg/beautyleg-170925-1506/1.html"
    url_image="https://img13.pixhost.org/images/224/52683532_1506-001.jpg"
    url="http://127.0.0.1:43110/1XRxFHFfa2UiXe46rVSGjfemtZycUny9g/image/qcwm-xiuren/list-1.html"  #xiuren
    #save_image(url_image,"22","555")
    #inm,p=get_cover(url)
    #for i in range(len(inm)):
        #print inm[i]+":"+p[i]
    #print get_name(url2)[0]
    girl_list=[]
    image_list=[]
    page_list=get_pagelink(url)
    for i in page_list:
        temp=get_handurl(url)+i
        girl_list.extend(get_onepage_girllink(temp))
        cover_list,place_list=get_cover(temp)
        print "start cover dowload %s"%(i)
        for i in range(len(cover_list)):
            save_image(cover_list[i],place_list[i],"00")
        print "wait for down cover"
    print "down all cover---start down pic"
    p_count=0
    p_flag=True
    #p.apply_async(test,args=(1,))
    for i in girl_list:
        #print "down %s"%(i)
        #save_girl(i,url)
        if p_count==0:
            p=Pool(15)
            p_flag=True
            print "start one"
        if p_count<15:
            print "down %s"%(i)
            p.apply_async(save_girl,args=(i,url,))
            p_count=p_count+1
        if p_count==15:
            print "waiting for ....."
            p.close()
            p.join()
            p_count=0
            p_flag=False
            print "down 5 girls  ....."
    if p_flag:
        p.close()
        p.join()


'''

    #print context2
    #text="63/1.html\"><img src=\"https://img14.pixhost.org/images/498/57405495_mygirl-170925-263-cover.jpg\" alt=\"\" title=\"[MyGirl-170925-263] 于大乔\" /></a>"
    #inm=get_imagelink(url2)
    #logging.info("2222")
'''
