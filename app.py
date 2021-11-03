from flask import Flask, request, make_response, jsonify
import jwt
import random
import json

app = Flask('advisor network API')

class save_data:
    def __init__(self,data):
        self.data = data#{"Advisors":{}, "Users":{}}
    def add_advisor(self,Advisor_Name=None,Advisor_Photo_URL=None):
        try:
            if self.data["Advisors"][f"{Advisor_Name}"] is None:
                self.data["Advisors"][f"{Advisor_Name}"] = {
                    "Advisor_ID":f"{Advisor_Name}_{random.randint(100,200)}",
                    "Advisor_Photo_URL":f"{Advisor_Photo_URL}"}
            else:
                pass
        except:
            self.data["Advisors"][f"{Advisor_Name}"] = {
                "Advisor_ID":f"{Advisor_Name}_{random.randint(100,200)}",
                "Advisor_Photo_URL":f"{Advisor_Photo_URL}"}
            return 
    def add_user(self,User_Name=None,User_Email=None,User_Password=None,User_id=None,JWT=None):
        try:
            if self.data["Users"][f"{User_Email}"] is None:
                self.data["Users"][f"{User_Email}"] = {
                    "User_id":f"{User_id}",
                    "User_Name":f"{User_Name}",
                    "User_Password":f"{User_Password}",
                    "JWT_Authentication_Token":f"{JWT}",
                    "Bookings": {} 
                }
            else:
                pass
        except:
            self.data["Users"][f"{User_Email}"] = {
                    "User_id":f"{User_id}",
                    "User_Name":f"{User_Name}",
                    "User_Password":f"{User_Password}",
                    "JWT_Authentication_Token":f"{JWT}",
                    "Bookings":{}
                }
    def add_booking(self,advisor_id,user_id,booking_time,booking_id):
        for ad_id in list(self.data['Advisors'].keys()):
            if self.data['Advisors'][ad_id]['Advisor_ID'] == advisor_id:
                advisor_details = {**{"Advisor_name" : ad_id} , **self.data['Advisors'][ad_id]}
                break
            else:
                pass
        
        for id in list(self.data['Users'].keys()):
            if self.data['Users'][id]['User_id'] == user_id:
                    self.data['Users'][id]['Bookings'] = {booking_id : {'Booking_time':booking_time, 'Advisor_detail':advisor_details}}
                    break
            else:
                pass
        


with open('Test_Data.json','r') as data:
    object = json.load(data)
savedata = save_data(object)

@app.route('/') 
def main_page():
    return "<pre><h1>API Working Great</h1>\
        <table>Change route to use api service:\
        <tr><td>1</td> <td>/admin/advisor/</td> <td> - To add an advisor </td>\
        <tr><td>2</td> <td>/user/register/</td> <td> - To register as a user </td>\
        <tr><td>3</td> <td>/user/login/</td> <td> - To log in as a user </td>\
        <tr><td>4</td> <td>/user/{user-id}/advisor </td> <td> - To Get the list of advisors </td>\
        <tr><td>5</td> <td>/user/{user-id}/advisor/{advisor-id}/</td> <td> - To book call with an advisor </td>\
        <tr><td>6</td> <td>/user/{user-id}/advisor/booking/</td> <td> - To get all the booked calls </td>\
        </table>\
        </pre>"

@app.errorhandler(400)
def bad_request_error():
    return  "400_BAD_REQUEST", 400

@app.route('/admin/advisor/',methods=['POST']) #/admin/advisor/?Name=kartik&Photo_URL="http://mypic.com"
def admin():
    Advisor_Name = request.args.get("Name")
    Advisor_Photo_URL = request.args.get("Photo_URL")
    if Advisor_Name is None or Advisor_Photo_URL is None:
        return make_response(bad_request_error())
    else:
        data = savedata.add_advisor(Advisor_Name,Advisor_Photo_URL)
        #print(savedata.data)
        return jsonify(savedata.data)#make_response("200_OK")

@app.route('/user/register/',methods=['POST'])
def user_register():
    Name = request.args.get("Name")
    Email = request.args.get("Email")
    Password = request.args.get("Password")
    if Name is None or Email is None or Password is None:
        return make_response(bad_request_error())
    else:
        payload = {
            'Name':f'{Name}',
            'Email':f'{Email}'
            }
        JWT = jwt.encode(payload,Password,algorithm='HS256')
        userid = f"{Name}_{random.randint(100,200)}"
        savedata.add_user(Name,Email,Password,userid,JWT)
        return jsonify({"Body":{"JWT_Authentication_Token": JWT, "User_ID": userid}, "Status": "200_OK"})

@app.route('/user/login/',methods=['POST'])
def user_login():
    Email = request.args.get("Email")
    Password = request.args.get("Password")
    if Email is None or Password is None:
        return make_response(bad_request_error())
    else:
        token = savedata.data['Users'][f'{Email}']['JWT_Authentication_Token']
        try:
            res = jwt.decode(token,key=Password,algorithms=['HS256'])
            return jsonify({"Body":
            {"JWT_Authentication_Token":f"{savedata.data['Users'][res['Email']]['JWT_Authentication_Token']}",
            "User_ID":f"{savedata.data['Users'][res['Email']]['User_id']}"},
            "Status":"200_OK"})
        except:
            return make_response("401_AUTHENTICATION_ERROR")

@app.route('/user/<user_id>/advisor/',methods=['GET'])
def List_advisors(user_id):
    return jsonify({"Body":
    {"Advisors Names":savedata.data["Advisors"]},
     "Status" : "200_OK"})

@app.route('/user/<user_id>/advisor/<advisor_id>/',methods=['POST'])
def Book_call(user_id,advisor_id):
    booking_time = request.args.get("Time")
    booking_id = f"{user_id}_{advisor_id}_{random.randint(100,200)}"
    savedata.add_booking(advisor_id,user_id,booking_time,booking_id)
    return make_response("200_OK")

@app.route('/user/<user_id>/advisor/booking/',methods=['GET'])
def Booked_calls(user_id):
    for id in list(savedata.data['Users'].keys()):
            if savedata.data['Users'][id]['User_id'] == user_id:
                    return jsonify( {"body" : savedata.data['Users'][id]['Bookings'], "Status": "200_OK"})
            else:
                pass
            
if __name__ == "main":
    app.run(debug=True)
