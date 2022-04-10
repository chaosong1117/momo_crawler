# import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import time
import json

class Momo_app():
    def __init__(self):
        pass

    def read_url_json(self, file):
        with open (file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # print(data)    
        return data

    def requests_url(self, url):
        url = url
        url_headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
        res = requests.get(url, headers = url_headers)
        # print(res.status_code)    #檢查是否取得網頁的資訊
        # print(res.text)
        
        soup = BeautifulSoup(res.text, 'lxml')
        time.sleep(1)
        return soup

    def get_class_url(self, data):
        res = []
        
        for sort in data:
            sort_class_dict = {}
            class_level1_list = []
            sort_name = sort["sort_name"]
            print(sort_name)
            sort_url = sort["sort_url"]
            sort_class_dict["sort_name"] = sort_name
            sort_class_dict["sort_url"] = sort_url

            # 取得第一層分類
            if sort_name != "首頁" and sort_name != "看看買":
                sort_soup = self.requests_url(sort_url)
                print(sort_url)
                time.sleep(2)
                class_level1_list = self.get_class_a_list(sort_soup)

                # 取得第二層分類
                for class_level1 in class_level1_list:
                    class_name = class_level1["class_name"].replace("/","-").replace("\\","-")
                    print(class_name)
                    class_level1_url = class_level1["class_url"]
                    class_level1_soup = self.requests_url(class_level1_url)
                    time.sleep(2)
                    class_level2_list = self.get_class_a_list(class_level1_soup)
                    # print(class_level2_list)
                    
                    for class_level2 in class_level2_list:
                        class_level2_url = class_level2["class_url"]
                        class_level2_soup = self.requests_url(class_level2_url)
                        time.sleep(2)
                        class_level3_list = self.get_class_a_list(class_level2_soup)
                        # print(class_level3_list)

                        for class_level3 in class_level3_list:
                            level3_url = class_level3["class_url"]
                            # print(class_level3["class_name"])

                            # 設定儲存檔案路徑
                            path = os.getcwd() + "\\class_url_txt\\" + sort_name + "\\"
                            if not os.path.exists(path):
                                os.makedirs(path)
                            
                            txt_name = path +class_name + ".txt"
                            if not os.path.isfile(txt_name):
                                print(level3_url)
                                self.write_url_txt(txt_name, level3_url)

                        class_level2["class_level3"] = class_level3_list
                    class_level1["class_level2"] = class_level2_list
                    # print(class_level1)
                    print(class_name + " 分類中的網址已取得")
                    print("")
                class_level1_list.append(class_level1)
                print(sort_name + " 種類中的網址已取得")
            sort_class_dict["class_level1"] = class_level1_list
            # print(sort_class_dict)
            res.append(sort_class_dict)
        # print(res)
        return res
    
    def get_class_a_list(self, soup):
        try:
            class_list = []
            class_tag_list = soup.find(class_ = "classificationArea jsCategoryList")
            class_a_list = class_tag_list.find_all("a")
            for class_a in class_a_list:
                class_dict  = {}
                class_dict["class_name"] = class_a.text
                class_dict["class_url"] = "https://m.momoshop.com.tw/category.momo?cn=" + class_a["subcatecode"]
                # print(class_dict)
                class_list.append(class_dict)
        except Exception as e:
            print(e)
            pass
        return class_list

    def write_url_txt(self, txt_name, url):
        with open(txt_name, "a", encoding="utf8") as f:
            f.write(url + "\n")


    def write_json(self, data):
        res = self.get_class_url(data)
        with open("app_class_url2.json", "w", encoding="utf8") as f:
            json.dump(res,f, ensure_ascii=False,indent=4)


if __name__ == '__main__':
    momo = Momo_app()
    file_name = "app_sort_url.json"
    data = momo.read_url_json(file_name)
    # momo.get_class_url(data)
    momo.write_json(data)


