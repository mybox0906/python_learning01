import requests
import re
import pymysql
import warnings

class LianjiaSpider:
    def __init__(self):
        self.baseurl = "https://bj.lianjia.com/ershoufang/pg"
        self.page = 1
        self.headers = {"User-Agent":"Mozilla/5.0"}
        self.proxies = {"http":"http://309435365:szayclhp@123.206.119.108:16817"}
        self.db = pymysql.connect("localhost",
                  "root","123456",charset="utf8")
        self.cursor = self.db.cursor()

    def getPage(self,url):
        res = requests.get(url,proxies=self.proxies,headers=self.headers,timeout=5)
        res.encoding = "utf-8"
        html = res.text
        print("页面爬取成功,正在解析...")
        self.parsePage(html)

    def parsePage(self,html):
        p = re.compile('<div class="houseInfo".*?data-el="region">(.*?)</a>.*?<div class="totalPrice">.*?<span>(.*?)</span>(.*?)</div>',re.S)
        r_list = p.findall(html)
        # [("天通苑","480","万"),()..]
        print("页面解析完成,正在存入数据库...")
        self.writeTomysql(r_list)

    def writeTomysql(self,r_list):
        c_db = "create database if not exists Lianjiadb \
                character set utf8"
        u_db = "use Lianjiadb"
        c_tab = "create table if not exists housePrice( \
                 id int primary key auto_increment,\
                 housename varchar(50), \
                 totalprice int)charset=utf8"
        
        warnings.filterwarnings("ignore")
        try:
            self.cursor.execute(c_db)
            self.cursor.execute(u_db)
            self.cursor.execute(c_tab)
        except Warning:
            pass

        ins = "insert into housePrice(housename,totalprice) \
               values(%s,%s)"
        for r_tuple in r_list:
            name = r_tuple[0].strip()
            price = float(r_tuple[1].strip())*10000
            L = [name,price]
            self.cursor.execute(ins,L)
            self.db.commit()
        print("存入数据库成功")


    def workOn(self):
        while True:
            c = input("爬取按y(q退出):")
            if c.strip().lower() == "y":
                url = self.baseurl + str(self.page) + "/"
                self.getPage(url)
                self.page += 1
            else:
                self.cursor.close()
                self.db.close()
                print("爬取结束,谢谢使用!")
                break



if __name__ == "__main__":
    spider = LianjiaSpider()
    spider.workOn()