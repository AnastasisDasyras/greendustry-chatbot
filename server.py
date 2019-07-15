from flask import Flask, request, jsonify
import json
import requests
import os
import smtplib, ssl

app = Flask(__name__)
port = int(os.environ["PORT"])
print(port)


@app.route('/', methods=['POST'])
def index():
    TOMATO_VALUE = 1.4
    CUCUMBER_VALUE = 1.25
    CARROT_VALUE = 1
    PEPPER_VALUE = 1.9
    flag = False
    kilos_flag = False
    info_flag = False
    # update data from thingspeak
    read_orders = requests.get(
        'https://api.thingspeak.com/channels/819280/feeds.json?api_key=O0DH98MWTHDMNX57&results=1000')

  # get data from chatbot
    data = json.loads(request.get_data())
  # get data from thing speak
    orders = json.loads(read_orders.text)
    orders_num = orders['channel']['last_entry_id']
    my_stock = orders['feeds'][int(orders_num)-1]['field1']
    stock_info = [x.strip() for x in my_stock.split(',')]
    tomato_stock = stock_info[-4]
    cucumber_stock = stock_info[-3]
    carrot_stock = stock_info[-2]
    pepper_stock = stock_info[-1]


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
                    # some locations have more information
                    i = 1
                    while (not('@' in infos[3+i])):
                        location = location + ', ' + infos[3+i]
                        i = i + 1
                    email = infos[-10]
                    zipcode = infos[-9]
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
                custid = 'abcd00'+str(int(orders_num+1))
            elif(len(str(orders_num)) == 2):
                custid = 'abcd0' + str(int(orders_num+1))
            else:
                custid = 'abcd' + str(int(orders_num+1))

            status = 'ready to be shipped'
            vegetable = data['conversation']['memory']['veg']['value']
            kilos = data['conversation']['memory']['num']['raw']
            flag = True

        #check kilos are asked with stock and update values
        if(vegetable=='tomato'):
            if(int(kilos) < int(stock_info[-4])):
                kilos_flag = True
                tomato_stock = int(stock_info[-4]) - int(kilos)
        elif(vegetable=='cucumber'):
            if((int(kilos) < int(stock_info[-3]))):
                kilos_flag = True
                cucumber_stock = int(stock_info[-3]) - int(kilos)
        elif(vegetable=='carrot'):
            if((int(kilos) < int(stock_info[-2]))):
                kilos_flag = True
                carrot_stock = int(stock_info[-2]) - int(kilos)
        else:
            if((int(kilos) < int(stock_info[-1]))):
                kilos_flag = True
                pepper_stock = int(stock_info[-1]) - int(kilos)

        # Send email alert about low stock
        if(int(tomato_stock)<=3000 or int(cucumber_stock)<=3000 or int(carrot_stock)<=3000 or int(pepper_stock)<=3000):
            gport = 465  # For SSL
            smtp_server = "smtp.gmail.com"
            sender_email = "greendustry4.0@gmail.com"  # Enter your address
            receiver_email = "anastasisdasy@gmail.com"  # Enter receiver address
            password = 'SpanosDasyras12'
            tom = cuc = car = pep = False
            if(int(tomato_stock)<=3000):
                tom = True
            if(int(cucumber_stock)<=3000):
                cuc = True
            if(int(carrot_stock)<=3000):
                car = True
            if(int(pepper_stock)<=3000):
                pep = True
            if(tom and cuc and car and pep):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes, cucumbers, carrots and peppers. Our stocks are very low."""
            elif(tom and cuc and car):
                 #two line breaks separate header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes, cucumbers and carrots. Our stocks are very low."""
            elif(tom and cuc and pep):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes, cucumbers and peppers. Our stocks are very low."""
            elif(tom and pep and car):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes, peppers and carrots. Our stocks are very low."""
            elif(pep and cuc and car):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order peppers, cucumbers and carrots. Our stocks are very low."""
            elif(tom and cuc):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes and cucumbers. Our stocks are very low."""
            elif(pep and cuc):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order peppers and cucumbers. Our stocks are very low."""
            elif(car and cuc):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order carrots and cucumbers. Our stocks are very low."""
            elif(tom and car):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes and carrots. Our stocks are very low."""
            elif(tom and pep):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes and peppers. Our stocks are very low."""
            elif(car and pep):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order carrots and peppers. Our stocks are very low."""
            elif(tom):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order tomatoes. Our stock is very low."""
            elif(cuc):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order cucumbers. Our stock is very low."""
            elif(car):
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order carrots. Our stock is very low."""
            else:
                 #one line break separates header from body
                message = """\
                Subject: STOCK ALERT

                We need to order peppers. Our stock is very low."""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, gport) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
        #make the only flag left true to show the wright message
        info_flag = True
        # create new orderid
        if(flag and kilos_flag):
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


            # create an order and save the client's info to thingspeak
            final_display = str(custid)+','+fullname+','+location+','+email + \
                ','+zipcode+','+status+','+orderid+','+vegetable+','+kilos+','+str(tomato_stock)+','+str(cucumber_stock)+','+str(carrot_stock)+','+str(pepper_stock)
            payload = {'api_key': 'P7P4BWK57W19AG1J', 'field1': final_display}
            requests.post('https://api.thingspeak.com/update', params=payload)
            # display info of client on chatbot
            final_display = 'ORDER\n'+'Customer id: '+str(custid)+'\nFullname: '+fullname+'\nVegetable: '+vegetable+'\nkilos'+kilos+'Order id: '+orderid

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
                kilos_flag = True
                info_flag = True
                #break #We will remove break to take the final status of the order which will be updated randomly
    elif(data['conversation']['skill'] == 'order'):
        #show the warehouse stock
        flag = True
        kilos_flag = True
        info_flag = True
        final_display = 'Stock Availability in kilos: \nTomatoes: '+str(tomato_stock)+'\nCucumbers: '+str(cucumber_stock)+'\nCarrots: '+str(carrot_stock)+'\nPeppers: '+str(pepper_stock)
    #show how much cost the order
    elif(data['conversation']['skill'] == 'how-many-kilos'):
        if(data['conversation']['memory']['veg']['value']=='tomato'):
            total_cost = TOMATO_VALUE * float(data['conversation']['memory']['num']['raw'])
        elif(data['conversation']['memory']['veg']['value']=='cucumber'):
            total_cost = CUCUMBER_VALUE * float(data['conversation']['memory']['num']['raw'])
        elif(data['conversation']['memory']['veg']['value']=='carrot'):
            total_cost = CARROT_VALUE * float(data['conversation']['memory']['num']['raw'])
        else:
            total_cost = PEPPER_VALUE * float(data['conversation']['memory']['num']['raw'])
        total_cost = round(total_cost,2)
        final_display = 'Total cost: ' + str(total_cost)
        flag = True
        kilos_flag = True
        info_flag = True
    
    # randomly change orders' status TO-DO

    if not(flag):
        final_display = 'Sorry something went wrong in your order. Please check your customer id'
    if not(kilos_flag):
        final_display = 'Sorry something went wrong in your order. Please check your order amount'
    if not(info_flag):
        final_display = 'Sorry something went wrong in your order. Please check your order id'
    return jsonify(status=200, replies=[{'type': 'text',
                                         'content': final_display}])


@app.route('/errors', methods=['POST'])
def errors():
  print(json.loads(request.get_data()))
  return jsonify(status=200)
  
app.run(port=port, host="0.0.0.0")
