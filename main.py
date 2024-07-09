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
    response = check_command(command)
    return {"response": response}





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
    return com,address,ago,cnt,trf,Km,NK


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







