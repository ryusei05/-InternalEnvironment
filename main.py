"""
micro:bit で環境光、温度の値を取得してambientに送信する
"""

from typing import Dict, List

import datetime
import ambient
import serial
import slackweb


def ambient_send(obj_ambient, d):
    """
    Ambient に環境光、温度の値を送信します
    """
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(dt)
    a = d.split(':')
    am_data: List[Dict[str, int]] = [{'d1': int(a[1]), 'd2': int(a[3])}]
    print(am_data)

    r = obj_ambient.send(am_data)

    print(r)


am = ambient.Ambient(1234, 'キー値')
ser = serial.Serial('COM3', 115200)

FROM_TIME = datetime.time(9, 30, 00)
TO_TIME = datetime.time(22, 00, 00)
HYPHEN = '-'
PRESET_TEMPERATURE = 27
line = ''
microbitdata = ''
date = datetime.datetime.now()
# アプリ起動 年月日取得
ymd = datetime.date(date.year, date.month, date.day)
# その日、Slackに投稿済みか？（1日1回だけ投稿するためのフラグ）
day_slack_alert = False
while True:
    # microbitからシリアル通信で読み出す（microbit側で1分一時停止している）
    line = ser.readline()
    # 現在日時取得
    diff_date = datetime.datetime.now()

    diff_ymd = datetime.date(diff_date.year, diff_date.month, diff_date.day)
    str_date = diff_date.strftime('%Y/%m/%d %H:%M:%S')
    print(str_date + '：' + line.decode('utf-8').strip())

    # microbitから温度と環境光の値を取得した
    if HYPHEN == line.decode('utf-8').strip():
        try:
            # 現在時刻取得
            time = diff_date.time()
            # 9:30～22:00 且つ 本日 Slack通知済みではない
            if FROM_TIME <= time <= TO_TIME and day_slack_alert is False:
                print(str_date + '：定時内')
                data = microbitdata.split(':')
                # 27℃以上
                if PRESET_TEMPERATURE <= int(data[1]):
                    day_slack_alert = True
                    # 平日の場合のみSlack投稿（祝日考慮はしない）
                    if diff_date.weekday() != 5 and diff_date.weekday() != 6:
                        if 6 >= diff_date.month <= 11:
                            # 6月、7月、8月、9月、10月、11月
                            msg = '社内の気温が' + data[1] + '℃になったよ。暑くない？窓際のエアコンをONにしてね。'
                        else:
                            # 12月、1月、2月、3月、4月、5月
                            msg = '社内の気温が' + data[1] + '℃になったよ。暑くない？エアコンの温度を調整してね。'
                        # slack に投稿
                        slack = slackweb.Slack(
                            url="https://hooks.slack.com/services/ヒ・ミ・ツ")
                        slack.notify(text=msg)
                        print(str_date + '：Slackに投稿[' + msg + ']')
                    else:
                        print(str_date + '：土日だよ')
            # 日替わり？
            elif ymd < diff_ymd:
                print(str_date + '：日付が変わった')
                ymd = diff_ymd
                day_slack_alert = False

            # Ambientに温度と環境光の値を送る
            # ambient_send(am, microbitdata)

            microbitdata = ''
            print('+++++++++++++++++++++++++++++++++++++++++++')
        except ValueError:
            print("Oops!  Try again...")
    else:
        microbitdata = microbitdata + line.decode('utf-8').strip() + ':'
ser.close()
