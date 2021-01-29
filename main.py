import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from tqdm import tqdm

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


FQDN = "https://photo.xuite.net/"
# 輸入你想要的相簿名稱
albumName = "ntuhwatermelon"
# albumName = "tsaibill5838"

albumPages = 1  # 預設相簿頁數
DownloadPath = "D:\\"  # 預設相簿路徑
LocalFolder = ""


# HTML頁面Parse
def parse_page(urlpage):
    response = requests.get(urlpage)  # 將網頁資料GET下來
    soup = BeautifulSoup(response.text, "html.parser")  # 將網頁資料以html.parser
    return soup


# 下載時顯示進度條
def download(url):
    filename = url.split('/')[-1]
    parseResult = urlparse(url)
    savefile = LocalFolder + "\\" + filename

    # print(savefile)

    if CheckFile(savefile) == False:
        try:
            img = requests.get(url)
            content_size = int(img.headers['Content-Length']) / 1024
            with open(savefile, "wb") as file:  # 開啟資料夾及命名圖片檔
                for data in tqdm(iterable=img.iter_content(1024), total=content_size, unit='k', desc=savefile):
                    file.write(img.content)  # 寫入圖片的二進位碼
                # print("Download File:" + savefile + " Complete")
        except:
            print("Download Fail:" + savefile)
    else:
        print(savefile + " File already exist.")


# 取得相簿分頁
def get_album(albumName):
    global albumPages, LocalFolder  # access global variable
    if not albumName:
        print("未輸入相簿名稱")
        return
    url = FQDN + albumName

    albumPages = get_MaxPage(url)  # 取得共有幾本相簿
    print("相簿" + albumName + "共" + albumPages + "頁相本")
    # 檢查目錄是否存在
    LocalFolder = DownloadPath + albumName
    CheckFolder(LocalFolder)

    parseResult = urlparse(url)

    # 進行每一頁相簿擷取
    for single in range(int(albumPages)):
        page = (parseResult.geturl() + "*" + str(single + 1))
        Get_albumPage(page)


def CheckFile(LocalFile):
    # 檢查檔案是否存在
    if os.path.isfile(LocalFile):
        return True
    else:
        return False


# 檢查目錄是否存在，若不存在則建立
def CheckFolder(LocalFolder):
    if os.path.isdir(LocalFolder):
        # print("目錄" + LocalFolder + "已存在")
        pass
    else:
        # print("產生" + LocalFolder + "目錄")
        os.makedirs(LocalFolder)


# 取得相簿分頁內容
def Get_albumPage(url):
    parseResult = urlparse(url)
    soup = parse_page(url)
    sel = soup.select("p.album_info_title > a")
    # count = 0
    for single in sel:
        linkpage = parseResult.scheme + ':' + single["href"]
        # if count == 0:
        Get_Photo(linkpage)
        # count += 1


# 判斷相簿頁面是否需要輸入密碼
def get_EncryptURL(url):
    content = parse_page(url)
    password = "23710148"  # 相簿密碼，目前版本只支援全部相簿密碼都一樣
    checkpwd = content.find(id="pwd")
    if checkpwd is not None:
        #####################################################
        # 這一段是從POSTMAN產出的
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pwd\"\r\n\r\n" + password + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'cache-control': "no-cache",
            'postman-token': "084ee711-0f42-de63-4507-d1eed28dbce9"
        }
        #####################################################
        response = requests.request("POST", url, data=payload, headers=headers)  # 取得輸入密碼後的頁面內容
        soup = BeautifulSoup(response.text, "html.parser")  # 將網頁資料以html.parser
        return soup
    else:  # 若不需要密碼直接回傳頁面內容
        return content


# 取得相片
def Get_Photo(url):
    global LocalFolder
    pages = str(get_MaxPage(url))  # 取得相簿分頁數

    content = get_EncryptURL(url)

    # 取得相簿名稱
    titleSoup = content.select("div.title > span.titlename > a:not(#nav-parent)")
    if titleSoup is not None:
        AlbumTitle = titleSoup[0].text
        LocalFolder = DownloadPath + albumName + "\\" + AlbumTitle
        CheckFolder(LocalFolder)
    else:
        print("titleSoup is None")

    # print("Pages: " + pages)
    for page in range(int(pages)):
        # response = requests.get(page["href"])  # 將網頁資料GET下來
        sel = content.select("div.photo_item.inline-block > a > img")

        for showdiv in sel:
            download(showdiv["src"].replace('_c', '_x'))


# 取得相簿帳號最大頁數
def get_MaxPage(url):
    MaxPage = 1
    page_content = parse_page(url)
    sel = page_content.select("div.page > #nav-last")
    # print(len(sel))

    if (len(sel) == 1):
        print(sel[0]["href"])
        SplitArr = sel[0]["href"].split('*')
        if (len(SplitArr) == 2):
            AlbumPage = SplitArr[1]
            MaxPage = SplitArr[1]
    return MaxPage


# Main Function
if __name__ == '__main__':
    get_album(albumName)
