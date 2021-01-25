import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import requests as req
from tqdm import tqdm


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


FQDN = "https://photo.xuite.net/"
# albumName = "ntuhwatermelon"
# albumName = "tsaibill5838"
albumPages = 1
DownloadPath = "D:\\"
LocalFolder = ""


# HTML頁面Parse
def parse_page(urlpage):
    response = requests.get(urlpage)  # 將網頁資料GET下來
    soup = BeautifulSoup(response.text, "html.parser")  # 將網頁資料以html.parser
    return soup


# 取得相簿分頁
def get_album(albumName):
    global albumPages, LocalFolder
    if not albumName:
        print("未輸入相簿名稱")
        return
    url = FQDN + albumName

    albumPages = get_MaxPage(url)  # 取得相簿最大頁面
    print("相簿" + albumName + "共" + albumPages + "頁")
    # 檢查目錄是否存在
    LocalFolder = DownloadPath + albumName
    CheckFolder(LocalFolder)

    parseResult = urlparse(url)
    # print("parseResult:" + parseResult.geturl())
    for single in range(int(albumPages)):
        page = (parseResult.geturl() + "*" + str(single + 1))

        Get_albumPage(page)
        # parse_page(page)


# 檢查目錄是否存在，若不存在則建立
def CheckFolder(LocalFolder):
    if os.path.isdir(LocalFolder):
        print("目錄" + LocalFolder + "已存在")
        pass
    else:
        print("產生" + LocalFolder + "目錄")
        os.makedirs(LocalFolder)


# 取得相簿分頁內容
def Get_albumPage(url):
    parseResult = urlparse(url)
    soup = parse_page(url)
    sel = soup.select("p.album_info_title > a")

    for single in sel:
        linkpage = parseResult.scheme + ':' + single["href"]
        # print("===Start Getting " + single.text +"==")
        pages = str(get_MaxPage(linkpage))
        print("「" + single.text + " " + parseResult.scheme + ':' + single["href"] + "」共" + pages + "頁")
        # print("===End of Getting " + single.text +"==")


# 取得相片
def Get_Photo(url):
    global LocalFolder
    soup = parse_page(url)
    password = "23710148"
    checkpwd = soup.find(id="pwd")
    if checkpwd is not None:
        print("請輸入密碼")

        # 這一段是從POSTMAN產出的
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pwd\"\r\n\r\n" + password + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'cache-control': "no-cache",
            'postman-token': "084ee711-0f42-de63-4507-d1eed28dbce9"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")  # 將網頁資料以html.parser
        # print(soup)
    else:
        print("不需要輸入密碼")
        # return soup

    # 取得頁數，但排除下一頁及最後一頁
    pages = soup.select("div.page > a:not(#nav-next, #nav-last)")

    titleSoup = soup.select("div.title > span.titlename > a:not(#nav-parent)")
    # text = soup.find("div.title > span.titlename > a")
    # 取得相簿名稱
    if len(titleSoup) == 1:
        AlbumTitle = titleSoup[0].text

    LocalFolder = DownloadPath + albumName + "\\" + AlbumTitle
    CheckFolder(LocalFolder)

    # Region 取得相簿中相片頁數
    print(len(pages) + 1)
    for page in pages:
        # print(page["href"])
        response = requests.get(page["href"])  # 將網頁資料GET下來
        sel = soup.select("div.photo_item.inline-block > a > img")
        count = 0

        for showdiv in sel:
            print(showdiv["alt"])

            print(showdiv["src"].replace('_c', '_x'))
            # response = requests.get(showdiv["src"].replace('_c', '_x'))
            if count == 0:
                print(showdiv["src"].replace('_c', '_x'))
                #download(showdiv["src"].replace('_c', '_x'))

            count += 1


# 取得相簿帳號最大頁數
def get_MaxPage(url):
    MaxPage = 1
    page_content = parse_page(url)
    sel = page_content.select("div.page > #nav-last")
    print(len(sel))

    if (len(sel) == 1):
        print(sel[0]["href"])
        SplitArr = sel[0]["href"].split('*')
        if (len(SplitArr) == 2):
            AlbumPage = SplitArr[1]
            MaxPage = SplitArr[1]
    return MaxPage

# 下載時顯示進度條
def download(url):
    #filename = url.split('/')[-1]
    parseResult = urlparse(url)
    savefile = LocalFolder + "\\" + parseResult.path
    r = req.get(url, stream=True)
    with open(savefile, 'wb') as f:
        for data in tqdm(r.iter_content(1024)):
            f.write(data)
    return savefile

# Press the green button in the gutter to run the script.
# Main Function
if __name__ == '__main__':
    albumName = "ntuhwatermelon"
    # get_album(albumName)
    page_inside = "https://photo.xuite.net/ntuhwatermelon/20546016"  # Need password
    Get_Photo(page_inside)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
