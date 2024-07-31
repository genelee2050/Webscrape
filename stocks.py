import json
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from wework_bot import WeBot


def main_loop():
    history = load_history()
    bot = WeBot()
    has_new_entry = False
    for key in get_search_keys():
        for entry in get_record_list(1, key):
            if entry["id"] not in history or entry["date"] != history[entry["id"]]["date"]:
                if entry["id"] in history and entry["date"] != history[entry["id"]]["date"]:
                    bot.send_text(format_msg(entry, only_date_updated=True))
                else:
                    bot.send_text(format_msg(entry))
                history[entry["id"]] = entry
                has_new_entry = True

    if has_new_entry:
        with open("saved_history.txt", "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)


def load_history():
    try:
        with open("saved_history.txt", "r", encoding="utf-8") as f:
            saved_history = json.load(f)
    except json.JSONDecodeError as e:
        saved_history = {}

    return saved_history


def get_search_keys():
    search_keys = []
    with open("search_keys.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            search_keys.append(line.strip())
    return search_keys


def get_record_list(page_num, search_key):
    url = "https://pccz.court.gov.cn/pcajxxw/searchKey/gjsslb"
    data = {"pageNum": page_num, "search": search_key}
    response = requests.post(url, json=data)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    data_list = []
    item_list = soup.find_all("div", {"class": "fd-datadiv"})
    for item in item_list:
        href_elem = item.find("a", {"class": "fd-search-title"})
        title = href_elem.get_text().strip()
        case_type, id = parse_ckxq(href_elem.get("onclick"))
        url = parse_url_type(case_type, id)
        date_elem = item.find("span", {"class": "fd-search-date"})
        date = parse_date(date_elem.get_text().strip())
        data_list.append({"search_key": search_key, "date": date, "title": title, "id": id, "url": url})

    return data_list


# other formats converted to yyyy-mm-dd
def parse_date(s):
    if re.match(r"\d{4}-\d{1,2}-\d{1,2}", s):
        return s
    else:
        return datetime.today().strftime("%Y-%m-%d")


def format_msg(entry, only_date_updated=False):
    if only_date_updated:
        s = f"{entry['search_key']} （仅时间有更新）\n{entry['date']}\n{entry['title']}\n{entry['url']}"
    else:
        s = f"{entry['search_key']}\n{entry['date']}\n{entry['title']}\n{entry['url']}"
    return s


def parse_ckxq(s):
    pattern = re.compile(r"ckxq\('(\w*)','(\w*)'\)")
    match = pattern.match(s)
    return match.group(1), match.group(2)


def parse_url_type(case_type, id):

    TYPE_URL_DIC = {
        "案件公告": "/pcgg/ggxq?id=",
        "其他公告": "/pcgg/ggxq?id=",
        "拍卖公告": "/pcgg/ggxq?id=",
        "招募投资人公告": "/pcgg/ggxq?id=",
        "债权人会议公告": "/pcgg/ggxq?id=",
        "招募管理人公告": "/pcgg/ggxq?id=",
        "重整计划草案": "/pcgg/ggxq?id=",
        "裁判文书": "/pcws/wsxq?id=",
        "新闻动态": "/pcnews/newsxq?id=",
        "便民指南": "/pcxwBmzn/bmznxq?cbh=",
        "预重整公告": "/yczgg/ggxq?yczgg=",
        "重整典型案例": "/pcdxal/dxalxq?id=",
        "法律法规": "/pcFlfg/flfgxq?id=",
        "实务文章": "/pcswwz/swwzxq?id=",
        "债务人信息": "/pczwr/zwrdh?id=",
        "公开案件": "/gkaj/gkajxq?id=",
    }

    CONTEXT = "https://pccz.court.gov.cn/pcajxxw"

    if case_type in TYPE_URL_DIC:
        url = CONTEXT + TYPE_URL_DIC[case_type] + id
        return url


if __name__ == "__main__":
    while True:
        try:
            main_loop()
            print("round complete")
            time.sleep(30)
        except requests.exceptions.ConnectionError:
            time.sleep(300)
        except Exception as e:
            print(e)
