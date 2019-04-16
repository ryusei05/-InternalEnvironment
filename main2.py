"""
weather:bit で温度、湿度を取得してDB(SQLite)に値を蓄積する
（可視化はmetabaseで確認する想定）
"""

import datetime
import serial

ser = serial.Serial('COM3', 115200)

HYPHEN = '-'
line = ''
microbitdata = ''
while True:
    # microbit(weather:bit)からシリアル通信で読み出す（microbit側で1分一時停止している）
    line = ser.readline()

    # microbit(weather:bit)から温度と環境光の値を取得した
    if HYPHEN == line.decode('utf-8').strip():
        try:
            data = microbitdata.split(':')
            # TODO: DB（SQLite）に蓄積
            now = datetime.datetime.now()

            microbitdata = ''
        except ValueError:
            print("Oops!  Try again...")
    else:
        microbitdata = microbitdata + line.decode('utf-8').strip() + ':'
ser.close()
