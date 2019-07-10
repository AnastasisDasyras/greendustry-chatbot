#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from tabulate import tabulate
import json
import requests

app = Flask(__name__)
port = '5000'


@app.route('/', methods=['POST'])
def index():
    # update data from thingspeak
    read_orders = requests.get(
        'https://api.thingspeak.com/channels/819280/feeds.json?api_key=O0DH98MWTHDMNX57&results=1000')

  # get data from chatbot
    data = json.loads(request.get_data())
    orders = json.loads(read_orders.text)
    orders_num = orders['channel']['last_entry_id']

  # order product
    if data['conversation']['memory']['inor']['value'] == 'order':
        if 'custid' in data['conversation']['memory']:
            custid = data['conversation']['memory']['custid']['raw']
            vegetable = data['conversation']['memory']['veg']['value']
            kilos = data['conversation']['memory']['num']['raw']
            # has to go to the thingspeak and get the data for custid

            for i in range(int(orders_num)):
                my_string = orders['feeds'][i]['field1']
                infos = [x.strip() for x in my_string.split(',')]
                if(custid == infos[0]):
                    fullname = infos[1]
                    location = infos[2] + ", " + infos[3]
                    # some location have more informaiton
                    i = 1
                    while (not('@' in infos[3+i])):
                        location = location + ', ' + infos[3+i]
                        i = i + 1
                    email = infos[-6]
                    zipcode = infos[-5]
                    status = 'ready to be shipped'
                    #print (infos[0]+" "+infos[1]+" "+infos[2]+" "+infos[3]+" "+infos[4]+" "+infos[5]+" "+vegetable+" "+kilos)
                    break
        else:
            fullname = data['conversation']['memory']['person']['fullname']
            location = data['conversation']['memory']['location']['formatted']
            email = data['conversation']['memory']['email']['raw']
            zipcode = data['conversation']['memory']['postal code']['raw']
            # create customer id
            if(len(str(orders_num)) == 1):
                custid = 'a00'+str(int(orders_num+1))
            elif(len(str(orders_num)) == 2):
                custid = 'a0' + str(int(orders_num+1))
            else:
                custid = 'a' + str(int(orders_num+1))

            status = 'ready to be shipped'
            vegetable = data['conversation']['memory']['veg']['value']
            kilos = data['conversation']['memory']['num']['raw']

        # create new orderid
        my_string = orders['feeds'][int(orders_num)-1]['field1']
        infos = [x.strip() for x in my_string.split(',')]
        previous_order = infos[-3].split('-')
        if(int(previous_order[1]) < 999):
            po = [int(previous_order[0]), int(previous_order[1])+1]
        else:
            po = [int(previous_order[0])+1, 0]
        if(len(str(po[1])) == 1):
            orderid = str(po[0])+"-00"+str(po[1])
        elif(len(str(po[1])) == 2):
            orderid = str(po[0])+"-0"+str(po[1])
        else:
            orderid = str(po[0])+"-"+str(po[1])

        # create an order and save the client's info
        final_display = str(custid)+','+fullname+','+location+','+email + \
            ','+zipcode+','+status+','+orderid+','+vegetable+','+kilos
        payload = {'api_key': 'P7P4BWK57W19AG1J', 'field1': final_display}
        requests.post('https://api.thingspeak.com/update', params=payload)

    # just need information
    else:
        flag = False
        # search the order
        for i in range(int(orders_num)):
            my_order = orders['feeds'][i]['field1']
            infolist = [x.strip() for x in my_order.split(',')]
            my_orderid = infolist[-3]
            if(my_orderid == data['conversation']['memory']['orderid']['value']):
                final_display = 'Your order status: ' + infolist[-4]
                flag = True
                break

    #randomly change orders' status

    return jsonify(status=200, replies=[{'type': 'text',
                                         'content': final_display}])


@app.route('/errors', methods=['POST'])
def errors():
    print json.loads(request.get_data())
    return jsonify(status=200)


app.run(port=port)
