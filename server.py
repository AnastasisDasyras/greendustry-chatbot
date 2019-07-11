from flask import Flask, request, jsonify
import json
import requests
import os

app = Flask(__name__)
port = int(os.environ["PORT"])
print(port)


@app.route('/', methods=['POST'])
def index():
    TOMATO_VALUE = 0.75
    CUCUMBER_VALUE = 0.5
    CARROT_VALUE = 0.7
    PEPPER_VALUE = 1.2
    flag = False
    # update data from thingspeak
    read_orders = requests.get(
        'https://api.thingspeak.com/channels/819280/feeds.json?api_key=O0DH98MWTHDMNX57&results=1000')

  # get data from chatbot
    data = json.loads(request.get_data())
    orders = json.loads(read_orders.text)
    orders_num = orders['channel']['last_entry_id']

  # order product
    if data['conversation']['memory']['inor']['value'] == 'order' and data['conversation']['skill'] == 'confirm-order':
        if 'custid' in data['conversation']['memory']:
            custid = data['conversation']['memory']['custid']['raw']
            vegetable = data['conversation']['memory']['veg']['value']
            kilos = data['conversation']['memory']['num']['raw']
            # has to go to the thingspeak and get the data for custid

            for i in range(int(orders_num)):
                my_string = orders['feeds'][i]['field1']
                infos = [x.strip() for x in my_string.split(',')]
                if(custid == infos[0]):
                    flag = True
                    fullname = infos[1]
                    location = infos[2] + ", " + infos[3]
                    # some location have more informaiton
                    i = 1
                    while (not('@' in infos[3+i])):
                        location = location + ', ' + infos[3+i]
                        i = i + 1
                    email = infos[-10]
                    zipcode = infos[-9]
                    status = 'ready to be shipped'
                    #print (infos[0]+" "+infos[1]+" "+infos[2]+" "+infos[3]+" "+infos[4]+" "+infos[5]+" "+vegetable+" "+kilos)
                    #break
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
            flag = True

        # create new orderid
        if(flag):
            my_string = orders['feeds'][int(orders_num)-1]['field1']
            infos = [x.strip() for x in my_string.split(',')]
            previous_order = infos[-7].split('-')
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
    elif (data['conversation']['skill'] == 'information'):
        # search the order
        for i in range(int(orders_num)):
            my_order = orders['feeds'][i]['field1']
            infolist = [x.strip() for x in my_order.split(',')]
            my_orderid = infolist[-7]
            if(my_orderid == data['conversation']['memory']['orderid']['value']):
                final_display = 'Your order status: ' + infolist[-8]
                flag = True
                break
    elif(data['conversation']['skill'] == 'order'):
        #show the warehouse stock
        my_stock = orders['feeds'][int(orders_num)-1]['field1']
        stock_info = [x.strip() for x in my_string.split(',')]
        tomato_stock = stock_info[-4]
        cucumber_stock = stock_info[-3]
        carrot_stock = stock_info[-2]
        pepper_stock = stock_info[-1]
        final_display = 'Availability: \nTomatoes: '+str(tomato_stock)+'\nCucumbers: '+str(cucumber_stock)+'\nCarrots: '+str(carrot_stock)+'\nPeppers: '+str(pepper_stock)

    # randomly change orders' status

    if not(flag):
        final_display = 'Sorry something went wrong in your order. Please check your customer id'
    return jsonify(status=200, replies=[{'type': 'text',
                                         'content': final_display}])


@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)
  
app.run(port=port, host="0.0.0.0")
