# -*- coding: utf-8 -*-
# python3
import pandas
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import codecs
import re

# 競馬場コード（スポーツナビ参照）
race_course_num = "05"
race_no = "10"
# 開催情報（1回東京1日→0101など）
race_date = "0212"

if race_course_num == "01":
    race_course = "札幌"
elif race_course_num == "02":
    race_course = "函館"
elif race_course_num == "03":
    race_course = "福島"
elif race_course_num == "04":
    race_course = "新潟"
elif race_course_num == "05":
    race_course = "東京"
elif race_course_num == "06":
    race_course = "中山"
elif race_course_num == "07":
    race_course = "中京"
elif race_course_num == "08":
    race_course = "京都"
elif race_course_num == "09":
    race_course = "阪神"
elif race_course_num == "10":
    race_course = "小倉"

out = codecs.open("./this_race_info.csv", "w", "sjis")
out.write("競馬場,レース番号,レース名,コース,周回,距離,馬場状態,枠番,馬番,馬名,性別,馬齢,毛色,調教師,馬体重,増減,斤量,騎手,人気,オッズ,調教コメント,調教評価\n")

race_html = urllib.request.urlopen(
    "http://keiba.yahoo.co.jp/race/denma/18" + race_course_num + race_date + race_no + "/")
race_soup = BeautifulSoup(race_html, "lxml")

# レース名の取得
race_name = race_soup.find_all("h1", class_="fntB")
race_name = re.sub(r"<[^>]*?>", "", str(race_name))
race_name = re.sub(r"[ \n\[\]]", "", str(race_name))
# 大阪-ハンブルグカップ対策
race_name = re.sub(r"—", "-", str(race_name))
# 19XX-19XXsダービーメモリーズ対策
race_name = re.sub(r"〜", "-", str(race_name))
# 重賞の回次を削除
race_name = re.sub(r"第.*?回", "", str(race_name))

# コース区分・距離の取得
race_info = race_soup.find_all("p", class_="fntSS gryB", attrs={'id': 'raceTitMeta'})
track = re.sub(r"\n", "", str(race_info))
track = re.sub(r" \[.*", "", str(track))
track = re.sub(r"[\[m]", "", str(track))
track = re.sub("・外", "", str(track))
track = re.sub("・内", "", str(track))
track = re.sub(r"・", " ", str(track))
track = re.sub(r" ", ",", str(track))
track = re.sub(r"<[^>]*?>", "", str(track))

# 馬場状態の取得
cond = race_soup.find_all("img", attrs={'width': '25'})
cond = re.sub(r"\[<img alt=\"", "", str(cond))
cond = re.sub(r"\" border.*$", "", str(cond))

horse_info = race_soup.find_all("td", class_="fntN")
horse_info = re.sub(r"<[^>]*?>", "", str(horse_info))
horse_info = re.sub(r",", "", str(horse_info))
horse_info = re.sub(r"毛 ", "毛,", str(horse_info))
# 石毛厩舎対策
horse_info = re.sub(r"石毛,", "石毛 ", str(horse_info))
horse_info = re.sub(r"牡", "牡,", str(horse_info))
horse_info = re.sub(r"牝", "牝,", str(horse_info))
horse_info = re.sub(r"せん", "せん,", str(horse_info))
horse_info = re.sub(r"/", ",", str(horse_info))
horse_info = re.sub(r"\n", ",", str(horse_info))
horse_info = re.sub(r"\) ,", ")\n", str(horse_info))
horse_info = re.sub(r", ,", "\n", str(horse_info))
horse_info = re.sub(r"[\[\]]", "", str(horse_info))
horse_info = re.sub(r"^,", "", str(horse_info))
horse_info = horse_info.split("\n")

weight_tax = race_soup.find_all("td", class_="txC")
weight_tax = re.sub(r"<[^>]*?>", "", str(weight_tax))
weight_tax = re.findall(r"[456][0-9]\.[05]", str(weight_tax))

weight = race_soup.find_all("td", class_="txC")
weight = re.sub(r"<[^>]*?>", "", str(weight))

# weight=[None]*len(horse_info)
weight = re.findall(r"[0-9][0-9][0-9]\(", str(weight))
weight = re.sub(r"\(", "", str(weight))
weight = re.sub(r"[\[\'\] ]", "", str(weight))
weight = weight.split(",")
# weight.insert(12,"NA")

# weight_change=[None]*len(horse_info)
weight_change = race_soup.find_all("td", class_="txC")
weight_change = re.sub(r"<[^>]*?>", "", str(weight_change))
weight_change = re.findall(r"\(.*\)", str(weight_change))
weight_change = re.sub(r"[\(\)\+]", "", str(weight_change))
weight_change = re.sub(r"[\[\'\] ]", "", str(weight_change))
weight_change = weight_change.split(",")
# weight_change.insert(12,"NA")

jockey = race_soup.find_all("a", href=re.compile("/directory/jocky"))
jockey = re.sub(r"<[^>]*?>", "", str(jockey))
jockey = re.sub(r"[\[\]]", "", str(jockey))
jockey = jockey.split(", ")

# オッズ、人気の取得
odds_url = "http://race.netkeiba.com/?pid=race_old&id=c2018" + race_course_num + race_date + race_no
odds_df = pandas.io.html.read_html(odds_url)

horse_gate = odds_df[0][0][3:]
horse_no = odds_df[0][1][3:]
odds = odds_df[0][9][3:]
popularity = odds_df[0][10][3:]
horse_gate_list = [0] * len(horse_gate)
horse_no_list = [0] * len(horse_no)
odds_list = [0] * len(horse_no)
popularity_list = [0] * len(horse_no)

j = 3
for i in horse_no:
    horse_gate_list[int(i) - 1] = horse_gate[j]
    horse_no_list[int(i) - 1] = horse_no[j]
    odds_list[int(i) - 1] = odds[j]
    popularity_list[int(i) - 1] = popularity[j]
    j += 1

# 調教評価の取得
train_url = "http://race.netkeiba.com/?pid=race_old&id=c2016" + race_course_num + race_date + race_no + "&mode=oikiri"
train_df = pandas.io.html.read_html(train_url)
train_comment = train_df[0][3][1:]
train_mark = train_df[0][4][1:]

train_comment_list = [0] * len(train_comment)
train_mark_list = [0] * len(train_mark)

j = 1
for i in range(1, len(train_mark_list) + 1):
    train_comment_list[int(i) - 1] = train_comment[j]
    train_mark_list[int(i) - 1] = train_mark[j]
    j += 1

for i in range(0, len(horse_info)):
    out.write(race_course + "," + race_no + "," + race_name + "," + track + "," + cond + "," + str(
        horse_gate_list[i]) + "," + str(horse_no_list[i]) + "," + str(horse_info[i]) + "," + str(weight[i]) + "," + str(
        weight_change[i]) + "," + str(weight_tax[i]) + "," + str(jockey[i]) + "," + str(popularity_list[i]) + "," + str(
        odds_list[i]) + "," + str(train_comment_list[i]) + "," + str(train_mark_list[i]) + "\n")

out.close()

# 出走馬の取得
start_url = 'http://keiba.yahoo.co.jp'
url_3 = '?d=1'
horses = race_soup.find_all("a", href=re.compile("/directory/horse"))
data_list = []
for horse in horses:
    url_2 = str(horse)[9:37]

    time.sleep(1)
    target_url = start_url + url_2 + url_3

    html = urllib.request.urlopen(target_url)
    soup = BeautifulSoup(html, "lxml")

    # 馬の名前を取得
    horse_name = soup.find("h1", {"class": "fntB"}).text
    print(horse_name)
    # idが"resultLs"であるtableタグを取得（このtableタグに欲しい情報がある）
    table = soup.find("table", {"id": "stakes"})

    # try,exceptで書いているのは、出走レース情報がない馬が存在するため
    try:
        # tableタグからtrタグをすべて取得
        trs = table.findAll("tr")
        for i, tr in enumerate(trs):
            # 1レースの情報を格納するリスト、先頭は馬の名前
            data = [horse_name]

            # 最初の行と最後の行はヘッダーなので飛ばす
            if i != 0 and i != len(trs):
                # trタグからtdタグをすべて取得
                tds = tr.findAll("td")
                for td in tds:
                    # dataに出走レースの情報を加えていく
                    d = td.text
                    data.append(d)
                # 1行のすべての情報をdataにappendしたらdata_listにappend
                data_list.append(data)
    except:
        continue

for d in data_list:
    print (d)
with open('./horse.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data_list)
