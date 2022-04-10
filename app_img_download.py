# import pandas as pd
from itertools import product
from bs4 import BeautifulSoup
import requests
import os
import time
import pymysql
from pymysql.converters import escape_string

class Momo_computer():
    def __init__(self):
        pass

    def read_url_txt(self, file):
        url_list = []
        with open (file, "r") as f:
            for line in f.readlines():
                url = line.replace("\n", "")
                # print(url)
                url_list.append(url)
        # print(url_list)
        return url_list
            

    def requests_url(self, url):
        url = url
        url_headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
        res = requests.get(url, headers = url_headers)
        # print(res.status_code)    #檢查是否取得網頁的資訊
        # print(res.text)
        
        soup = BeautifulSoup(res.text, 'lxml')
        time.sleep(1)
        return soup
    
    # 一件商品內容(名稱、圖片標題與網址)
    def get_one_commodity(self, com):
        commodity = {}
        
        # 產品名稱
        commodity["title"] = com.find(class_ = "prdName").text

        img_tag = com.find(class_="swiper-wrapper")
        img = img_tag.find("img")
        # 圖片標題
        commodity["img_name"] = str(img.get("title")).replace("/","-").replace("\\","-")
        # 圖片網址
        commodity["img_src"] = img.get("src")
        return commodity

    
    # 一個頁面的全部商品
    def get_one_page_all(self, url):
        page_dict = {}
        soup = self.requests_url(url)

        try:
            # 分類名稱
            class_tag = soup.find(class_="pathArea")
            class_name = ""
            for li in class_tag.find_all("li"):
                li_text = li.text.replace("\n", "").replace(" ", "")
                class_name += li_text
            page_dict["class_name"] = class_name
            # print(class_name)

            # 全部商品內容
            commodity_list = []
            for com in soup.find_all(class_ = "productInfo"):
                commodity_list.append(self.get_one_commodity(com))
            page_dict["commodity"] = commodity_list
            # print(len(commodity_list))
            # print(page_dict)
        except Exception as e:
            print(e)
            page_dict = {}
            # pass
        return page_dict
    
    # 判斷網頁是否有頁數，如果沒有就直接下載該頁，如果有就每頁都爬取
    def get_page_value(self, file_name):
        url_list = self.read_url_txt(file_name)
        for url in url_list:
            # print(url)
            try:
                # 爬第一次取得最後一頁頁碼
                soup = self.requests_url(url)
                page_tag = soup.find(class_="pageArea")
                if str(page_tag) != "None":
                    page = page_tag.find_all("a")
                    final_page = page[-1].text
                else:
                    final_page = 1
                # print(final_page)

                # 變更網址中pageNum的數字
                for i in range(1, int(final_page)+1):
                    new_url = url + "&page=" + str(i)
                    print(new_url)

                    # 取得頁面中的全部商品
                    print("第 "+str(i)+" 頁")
                    page_dict = self.get_one_page_all(new_url)
                    class_name = page_dict['class_name']
                    for commodity in page_dict['commodity']:
                        product_name = commodity['title']
                        image_name = commodity['img_name']
                        image_src = commodity['img_src']
                        self.insert_into_sql(class_name, product_name, image_name, image_src)
                    if page_dict != {}:
                        self.img_download(page_dict)
                        
            except Exception as e:
                print(e)
                # pass
                

    # 圖片下載
    def img_download(self, page_dict):
        # 取得分類名稱
        class_name = page_dict["class_name"].split(">")

        # 建立路徑
        path = os.getcwd() + "\\image\\" + class_name[1] + "\\"
        if not os.path.exists(path):
            os.makedirs(path)
        
        have_picture = 0
        # 取得每個產品的圖片網址並下載
        for commodity in page_dict["commodity"]:
            try:
                name = commodity["img_name"].replace("/","-").replace("\\","-")
                img_name = path + name + ".jpg"
                img_url = commodity["img_src"]

                if not os.path.isfile(img_name):
                    # print(name)
                    img_res = requests.get(img_url, stream=True)
                    time.sleep(0.5)
                    with open(img_name, "wb") as fp:
                        fp.write(img_res.content)
                else:
                    have_picture += 1
            except Exception as e:
                print(e)
                # pass
                
        print("已下載過的圖片 " + str(have_picture) + " 張")
        print("該頁下載完成\n")
    
    # 啟用資料庫
    def excute_sql_command(self, sql_command):
        db_settings = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "db": "momo_product",
            "charset": "utf8"
        }
        self.conn = pymysql.connect(**db_settings)

        with self.conn.cursor() as mycursor:
            mycursor.execute(sql_command)
            result = mycursor.fetchone()
        self.conn.commit()
        self.conn.close()
        return result

    def insert_into_sql(self, product_type, product_name, img_name, img_src):
        sql_command = (
            "INSERT INTO product "
            "(product_class, product_name, img_name, img_src, created_at, updated_at) "
            "VALUES ('{0}', '{1}', '{2}', '{3}', NOW(), NOW()) "
        ).format(escape_string(product_type), escape_string(product_name), escape_string(img_name), escape_string(img_src))
        self.excute_sql_command(sql_command)



 
if __name__ == '__main__':
    momo = Momo_computer()
    class_path = os.getcwd() + "\\class_url_txt\\"
    class_path_list = os.listdir(class_path)
    # print(class_path_list)
    for class_name in class_path_list:
        commodity_path = class_path + class_name + "\\"
        commodity_path_list = os.listdir(commodity_path)
        # print(commodity_path_list)

        for j in commodity_path_list:
            file_path = class_path + class_name + "\\" + j
            print(file_path)
            momo.get_page_value(file_path)


