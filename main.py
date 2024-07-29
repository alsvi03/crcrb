import json
import uuid
import datetime
import time
import sys
from fastapi import FastAPI, Body

# uvicorn main:app --reload

  # $body = @{
  #      command = "Hello World!"
  #  }
  #  Invoke-WebRequest -Uri http://127.0.0.1:8000/process_command -Method POST -Headers @{"Content-Type" = "application/json"; "Accept" = "application/json"} -Body ($body | ConvertTo-Json)
  #

#локальном хосте (127.0.0.1) и порту 8000
app = FastAPI()


@app.post("/process_command")
async def process_command(command: str = Body(...)):
   # response = f"Вы прислали команду: {command}"
    com, address, ago, cnt, trf, Km, NK,k1,k2 = check_command(command)
   # отправляю это все в базу
    response = create_answer(json_answer,address,com,k1,k2)
    return {"response": response}



#-------------------------------------
#пример ответа

#для day,incday,allen
json_answer = [{'time': '2024-07-01T14:15:00Z', 'ep': 1032434.8, 'em': 774.2, 'rp': 1847870.1, 'rm': 0.1, 'tarif': '0', 'vm_id': '7'},
               {'time': '2024-07-01T00:00:00Z', 'ep': 207243.9, 'em': 84.9, 'rp': 352913.7, 'rm': 0.1, 'tarif': '4', 'vm_id': '7'},
               {'time': '2024-07-01T00:00:00Z', 'ep': 721502.7, 'em': 328.5, 'rp': 1295172.4, 'rm': 0.1, 'tarif': '1', 'vm_id': '7'},
               {'time': '2024-07-01T00:00:00Z', 'ep': 227568.3, 'em': 55.0, 'rp': 401458.2, 'rm': 0.0, 'tarif': '3', 'vm_id': '7'}]
#-------------------------------------


tBufUART: bytearray = [0] * 40


#
# def ncp_getCRC(buff, size):  # подсчет контрольной суммы
#     POLYNOM = 0xA001
#     crc = 0xFFFF
#     pcBlock = buff
#
#     for i in range(0,size):
#         crc ^= pcBlock[i] << 8
#         for j in range(8):
#             if crc & 0x8000:
#                 crc = (crc << 1) ^ POLYNOM
#             else:
#                 crc = crc << 1
#     return crc


def ncp_addCRC(buff, size):  # добавление контрольной суммы в буфер
    crc = calcCRC(buff, size)
    buff[size] = (crc >> 8) & 0xff
    buff[size + 1] = crc & 0xff
    return size + 2


def calcCRC(BufUART, LenBufUART):
    CRC16b = 0xFFFF
    for j in range(LenBufUART):
        _Byte = BufUART[j]
        for i in range(8):
            check_flag = ((_Byte ^ CRC16b) & 0x01)
            CRC16b >>= 1
            _Byte >>= 1
            if check_flag == 1:
                CRC16b ^= 0xA001
    return CRC16b







def hex_to_int(buff):
    int_buf = [0]*len(buff)
    for i in range(len(buff)):
        int_buf[i]=int(buff[i],16)
    return int_buf

def process_string(input_string):  # приведение ответа к формату буфера
    buffer = []
    for i in range(0, len(input_string), 2):
        if i+1 < len(input_string):
            two_chars = input_string[i:i+2]
            num = two_chars
            buffer.append(num)

    return buffer

def int_to_hex(buff,size):
    for i in range(size):
            hexval = hex(buff[i])
            hexstr = hexval[2:]
            if len(hexstr) == 1:
                buff[i] = "0" + hexstr
            else:
                buff[i] = hexstr




def check_command(buff): #узнаем что у нас запрашивают

    buff = hex_to_int(process_string(buff)) #приводим строку к нормальному буферу

    if buff[5] == 0x40:
        com = 'incday'
    elif buff[5] == 0x42:
        com = 'incmonth'
    elif buff[5] == 0x54:
        com = 'min30'
    elif buff[5] == 0xf1:
        com = 'instant'
    elif buff[5] == 0x80:
        com = 'month'
    else:
        com = 'uncnown'


    address = int(buff[1])
    ago = int(buff[10])
    cnt = int(buff[11])
    trf = int(buff[13])
    Km = int(buff[7]) # номер счетчика *4 (4 вида энергии)
    NK = int(buff[9]) # кол-во видов энергии
    k1 = int(buff[14]) #код запроса
    k2 = int(buff[15])
    return com,address,ago,cnt,trf,Km,NK,k1,k2


def create_answer(json,address,com,k1,k2):
    global tBufUART
    tBufUART[0] = 0xc3 #начальный байт 55 для запроса, С3 для ответа
    tBufUART[1] = int(str(hex(address)[2:])[1:],16) #адрес
    tBufUART[2] = 0x00
    tBufUART[3] = 0x20 #кол-во байт в пакете
    tBufUART[4] = 0x00
    if com == 'incday':
        tBufUART[5] = 0x40 #Номер функции
    elif com == 'incmonth':
        tBufUART[5] = 0x42
    elif com == 'min30':
        tBufUART[5] = 0x54
    elif com == 'instant':
        tBufUART[5] = 0xf1
    elif com == 'month':
        tBufUART[5] = 0x80

    tBufUART[6] = 0x00 #данные 6-21
    tBufUART[7] = 0x00
    tBufUART[8] = 0x00
    tBufUART[9] = 0x00

    tBufUART[10] = 0x00
    tBufUART[11] = 0x00
    tBufUART[12] = 0x00
    tBufUART[13] = 0x00

    tBufUART[14] = 0x00
    tBufUART[15] = 0x00
    tBufUART[16] = 0x00
    tBufUART[17] = 0x00

    tBufUART[18] = 0x00
    tBufUART[19] = 0x00
    tBufUART[20] = 0x00
    tBufUART[21] = 0x00

    tBufUART[22] = 0x00 #Код достоверности

    time_string = json[0]["time"]
    date_part, time_part = time_string[:-1].split('T')
    year, month, day = date_part.split('-')
    hour, minute, second = time_part.split(':')

    tBufUART[23] = int(minute) #Минуты
    tBufUART[24] = int(hour) #Часы
    tBufUART[25] = int(day) #День
    tBufUART[26] = int(month) #Месяц
    tBufUART[27] = int(year) #Год

    tBufUART[28] = k1 #Код запроса, повторяющийся в ответ
    tBufUART[29] = k2

    tBufUART[30] = 0x00 #Контрольная сумма
    tBufUART[31] = 0x00

    ncp_addCRC(tBufUART, 30)
    tBufUART = tBufUART[:32]
    int_to_hex(tBufUART, 32)

    out = ""
    for i in range(len(tBufUART)):
        out += tBufUART[i]


    return out


def create_Packege(): #не нужен
    #55 01 00 12 00 40      00 01   00 04           00 03              00 03            00 02          91 1D
    #                                           | дней назад | нач и конеч тарифы |  код запроса | контрольная сумма
    global tBufUART
    tBufUART[0] = 0x55 #начальный байт 55 для запроса, С3 для ответа
    tBufUART[1] = 0x01 #адрес
    tBufUART[2] = 0x00
    tBufUART[3] = 0x12 #кол-во байт в пакете (18 = 12 в 16-ричной)
    tBufUART[4] = 0x00
    tBufUART[5] = 0x40 #код команды (40 - Приращение энергии за указанные сутки по выбранным каналам)
    tBufUART[6] = 0x00 #номер стартового канала
    tBufUART[7] = 0x01
    tBufUART[8] = 0x00 #количество запрашиваемых каналов
    tBufUART[9] = 0x04
    tBufUART[10] = 0x00 # текущие сутки
    tBufUART[11] = 0x03 # дней назад
    tBufUART[12] = 0x00  # начальный тариф
    tBufUART[13] = 0x00  # конечный тариф
    tBufUART[14] = 0x00  # код запроса
    tBufUART[15] = 0x01  # код запроса
    tBufUART[16] = 0x00  # контрольная сумма
    tBufUART[17] = 0x00  # контрольная сумма
    ncp_addCRC(tBufUART, 16)
    tBufUART = tBufUART[:18]
    int_to_hex(tBufUART,18)







