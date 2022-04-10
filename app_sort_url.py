from bs4 import BeautifulSoup
import requests
import time
import json

class Momo_app():
    def __init__(self):
        pass

    def requests_url(self, url):
        url = url
        url_headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
        res = requests.get(url, headers = url_headers)
        # print(res.status_code)    #檢查是否取得網頁的資訊
        # print(res.text)
        
        soup = BeautifulSoup(res.text, 'lxml')
        time.sleep(1)
        return soup
    
    # 取得手機版網頁內容
    def get_sort_url(self, url):
        res = []
        soup = self.requests_url(url)

        sort_tag_list = soup.find(class_ = "sortBtnArea")
        selects = sort_tag_list.find_all("li")
        # print(selects)
        for select in selects:
            select_dict = {}
            select_url = select.find("a")
            select_dict["sort_name"] = select_url.text.replace('/', '_')
            if select_url.text == "首頁":
                select_dict["sort_url"] = "https://m.momoshop.com.tw/main.momo"
            else:
                select_dict["sort_url"] = "https://m.momoshop.com.tw/" + select_url["href"]
            # print(select_dict)
            res.append(select_dict)
        # print(res)
        return res
    
    def write_json(self, url):
        res = self.get_sort_url(url)
        with open("app_sort_url.json", "w", encoding="utf8") as f:
            json.dump(res,f, ensure_ascii=False,indent=4)

if __name__ == '__main__':
    sort_txt = Momo_app()
    url = "https://m.momoshop.com.tw/main.momo"
    sort_txt.write_json(url)