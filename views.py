from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import json
from web3 import Web3, HTTPProvider
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import random
from datetime import date
import requests
from django.http import JsonResponse


global user, hospital
def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Organ.json' #Organ contract code
    deployed_contract_address = '0x27e5140045416e8cC042D04b4Fe89F7F9e42Ff9A' #hash address to access Organ contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'signup':
        details = contract.functions.getUser().call()
    if contract_type == 'donor':
        details = contract.functions.getDonor().call()
    if contract_type == 'patient':
        details = contract.functions.getPatient().call()
    elif contract_type == 'match_organs':  # New condition for fetching match organs data
        details = contract.functions.getMatchOrgans().call()
    print(details)    



def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Organ.json' #Organ contract file
    deployed_contract_address = '0x27e5140045416e8cC042D04b4Fe89F7F9e42Ff9A' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'signup':
        details+=currentData
        msg = contract.functions.addUser(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'donor':
        details+=currentData
        msg = contract.functions.setDonor(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'patient':
        details+=currentData
        msg = contract.functions.setPatient(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)       

def updateConsent(currentData, contract_type):
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Organ.json' #organ contract file
    deployed_contract_address = '0x27e5140045416e8cC042D04b4Fe89F7F9e42Ff9A' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    if contract_type == "donor":
        msg = contract.functions.setDonor(currentData).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    else:
        msg = contract.functions.setPatient(currentData).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def Alert(request):
    if request.method == 'GET':
        global user
        pid = request.GET.get('pid', False)
        did = request.GET.get('did', False)
        phone = request.GET.get('phone', False)
        request.session['donarcontact'] = phone
        print("==============================+")
        print(request.session['donarcontact'])
        record = ''
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] != pid:
                record += rows[i]+"\n"
            else:
                record += arr[0]+"#"+arr[1]+"#"+arr[2]+"#"+arr[3]+"#"+arr[4]+"#"+arr[5]+"#"+arr[6]+"#"+arr[7]+"#"+arr[8]+"#"+arr[9]+"#Donor "+did+" Matched\n"
        updateConsent(record, "patient")

        record = ''
        readDetails("donor")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] != did:
                record += rows[i]+"\n"
            else:
                record += arr[0]+"#"+arr[1]+"#"+arr[2]+"#"+arr[3]+"#"+arr[4]+"#"+arr[5]+"#"+arr[6]+"#"+arr[7]+"#"+arr[8]+"#"+arr[9]+"#Patients "+pid+" Matched\n"
        url = "https://www.fast2sms.com/dev/bulkV2"

        
        no = request.session['patientcontact']
        message="Congratulations, Patient! A compatible donor has been identified for you. Your patience and perseverance have led to this promising opportunity. We are here to support you through every stage of this journey."
        data1 = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": no,
        }
        headers = {
            "authorization": "",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data1)
        print(response)                
        updateConsent(record, "donor")
        url = "https://www.fast2sms.com/dev/bulkV2"

        # message = 'Hi ' + name + ' You voted successfully. Thank you for voting at ' + timeStamp + ' on ' + date + '.'
        no = phone
        message="Hello Donor, Your selfless act of donation has been matched with a patient in need. Your kindness and compassion are deeply appreciated. Please consider confirming your donation to proceed with this life-saving process."
        data1 = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": no,
        }
        headers = {
            "authorization": "",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=data1)
        print(response)
        context= {'data':"Alert Sent to both Patinet : "+pid+" & Donor : "+did+" About Matched"}
        return render(request, 'HospitalScreen.html', context)
                

def MatchOrganAction(request):
    if request.method == 'GET':
        global user
        pid = request.GET.get('pid', False)
        organs = request.GET.get('organs', False)
        contact = request.GET.get('contact', False)
        
        request.session['patientcontact'] = contact
        print("===========")
        print(request.session['patientcontact'])
        columns = ['Donor ID', 'Donor Name', 'Address', 'Contact No','Blood Group','Health Condition', 'Donating Organs', 'Aadhar No', 'Hospital', 'Entry Date', 'Alert User & Donor About Matching']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        readDetails("donor")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            # if arr[9] == 'Pending':
            output+='<tr><td>'+font+str(arr[0])+'</td>'
            output+='<td>'+font+str(arr[1])+'</td>'
            output+='<td>'+font+str(arr[2])+'</td>'
            output+='<td>'+font+str(arr[3])+'</td>'
            output+='<td>'+font+str(arr[4])+'</td>'
            output+='<td>'+font+str(arr[5])+'</td>'
            output+='<td>'+font+str(arr[6])+'</td>'
            output+='<td>'+font+str(arr[7])+'</td>'
            output+='<td>'+font+str(arr[8])+'</td>'
            output+='<td>'+font+str(arr[9])+'</td>'
            output+='<td><a href=\'Alert?pid='+str(pid)+'&did='+str(arr[0])+'&phone='+str(arr[3])+'\'><font size=3 color=black>Send Alert</font></a></td></tr>'                
        output += "<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>"
        context= {'data':output}
        return render(request, 'HospitalScreen.html', context)                 
        

def MatchOrgans(request):
    if request.method == 'GET':
        columns = ['Patient ID', 'Patient Name', 'Address', 'Contact No','Blood Group', 'Disease History', 'Required Organs', 'Aadhar No', 'Hospital', 'Entry Date', 'Match Organs']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
        # if arr[9] == 'Pending':
            output+='<tr><td>'+font+str(arr[0])+'</td>'
            output+='<td>'+font+str(arr[1])+'</td>'
            output+='<td>'+font+str(arr[2])+'</td>'
            output+='<td>'+font+str(arr[3])+'</td>'
            output+='<td>'+font+str(arr[4])+'</td>'
            output+='<td>'+font+str(arr[5])+'</td>'
            output+='<td>'+font+str(arr[6])+'</td>'
            output+='<td>'+font+str(arr[7])+'</td>'
            output+='<td>'+font+str(arr[8])+'</td>'
            output+='<td>'+font+str(arr[9])+'</td>'
            output+='<td><a href=\'MatchOrganAction?pid='+str(arr[0])+'&organs='+str(arr[6])+'&contact='+str(arr[3])+'\'><font size=3 color=black>Click Here to Match Organs</font></a></td></tr>'                
        output += "<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>"
        context= {'data':output}
        return render(request, 'HospitalScreen.html', context)

def ViewTransplant(request):
    if request.method == 'GET':
        columns = ['Patient ID', 'Patient Name', 'Address', 'Contact No','Blood Group', 'Disease History', 'Required Organs', 'Aadhar No', 'Hospital', 'Entry Date', 'Transplant Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if len(arr) >= 11 and arr[10] != 'Pending':
                output+='<tr><td>'+font+str(arr[0])+'</td>'
                output+='<td>'+font+str(arr[1])+'</td>'
                output+='<td>'+font+str(arr[2])+'</td>'
                output+='<td>'+font+str(arr[3])+'</td>'
                output+='<td>'+font+str(arr[4])+'</td>'
                output+='<td>'+font+str(arr[5])+'</td>'
                output+='<td>'+font+str(arr[6])+'</td>'
                output+='<td>'+font+str(arr[7])+'</td>'
                output+='<td>'+font+str(arr[8])+'</td>'
                output+='<td>'+font+str(arr[9])+'</td>'
                output+='<td>'+font+str(arr[10])+'</td></tr>'                
        output += "<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>"
        context= {'data':output}
        return render(request, 'HospitalScreen.html', context)

def ViewRequestStatus(request):
    if request.method == 'GET':
        global user
        columns = ['Patient ID', 'Patient Name', 'Address', 'Contact No','Blood Group', 'Disease History', 'Required Organs', 'Aadhar No', 'Hospital', 'Entry Date', 'Transplant Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        readDetails("patient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if user == arr[0]:
                output+='<tr><td>'+font+str(arr[0])+'</td>'
                output+='<td>'+font+str(arr[1])+'</td>'
                output+='<td>'+font+str(arr[2])+'</td>'
                output+='<td>'+font+str(arr[3])+'</td>'
                output+='<td>'+font+str(arr[4])+'</td>'
                output+='<td>'+font+str(arr[5])+'</td>'
                output+='<td>'+font+str(arr[6])+'</td>'
                output+='<td>'+font+str(arr[7])+'</td>'
                output+='<td>'+font+str(arr[8])+'</td>'
                output+='<td>'+font+str(arr[9])+'</td>'
                output+='<td>'+font+str(arr[10])+'</td></tr>'                
        output += "<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def DonationStatus(request):
    if request.method == 'GET':
        global user
        pid = request.GET.get('pid', False)
        organs = request.GET.get('organs', False)
        columns = ['Donor ID', 'Donor Name', 'Address', 'Contact No', 'Blood Group', 'Health Condition', 'Donating Organs', 'Aadhar No', 'Hospital', 'Entry Date', 'Match Status']
        output = "<table border=1 align=center>"
        font = '<font size="" color="black">'
        for i in range(len(columns)):
            output += '<th>'+font+columns[i]+'</th>'
        output += "</tr>"
        readDetails("donor")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if len(arr) > 0 and user == arr[0]:
                output+='<tr><td>'+font+str(arr[0])+'</td>'
                output+='<td>'+font+str(arr[1])+'</td>'
                output+='<td>'+font+str(arr[2])+'</td>'
                output+='<td>'+font+str(arr[3])+'</td>'
                output+='<td>'+font+str(arr[4])+'</td>'
                output+='<td>'+font+str(arr[5])+'</td>'
                output+='<td>'+font+str(arr[6])+'</td>'
                output+='<td>'+font+str(arr[7])+'</td>'
                output+='<td>'+font+str(arr[8])+'</td>'
                output+='<td>'+font+str(arr[9])+'</td>'
                output+='<td>'+font+str(arr[10])+'</td></tr>'                
        output += "<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>"
        context= {'data':output}
        return render(request, 'DonorScreen.html', context) 

def send_sms(phone, message):
    """
    Function to send SMS notification.
    :param phone_number: Phone number to which SMS should be sent.
    :param id: ID of the added donor/patient.
    """
    # Replace API_KEY with your actual API key obtained from the SMS service provider
    api_key = ""
    url = "https://www.fast2sms.com/dev/bulkV2"
    no = phone
    data = {
        "route": "q",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": no,
    }
    headers = {
        "authorization": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("SMS notification sent successfully.")
    else:
        print("Failed to send SMS notification.")

def check_aadhar_exists(aadhar, entity):
    """
    Function to check if Aadhar number already exists.
    :param aadhar: Aadhar number to check.
    :param entity: Entity to check (donor or patient).
    :return: True if Aadhar number already exists, False otherwise.
    """
    readDetails(entity)
    rows = details.split("\n")
    for row in rows:
        if aadhar in row:
            return True
    return False
def check_contact_exists(contact, entity):
    """
    Function to check if contact number already exists.
    :param contact: Contact number to check.
    :param entity: Entity to check (donor or patient).
    :return: True if contact number already exists, False otherwise.
    """
    readDetails(entity)
    rows = details.split("\n")
    for row in rows:
        if contact in row:
            return True
    return False

def AddDonorHistoryAction(request):
    if request.method == 'POST':
        global hospital
        donor = request.POST.get('t1', False)
        address = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        condition = request.POST.get('t4', False)
        organs = request.POST.get('t5', False)
        aadhar = request.POST.get('t6', False)
        blood_group = request.POST.get('t7',False)
        today = date.today()
        readDetails("donor")
        rows = details.split("\n")

        if any(aadhar in row for row in rows):
            message = "Aadhar number already exists, Please try a new aadhar number."
            context = {'data': message}
            return render(request, 'AddDonorHistory.html', context)
        
        # if check_contact_exists(contact, "donor"):
        #     message = "Contact number already exists, Please try a new contact number."
        #     context = {'data': message}
        #     return render(request, 'AddDonorHistory.html', context)
        
        did = len(rows)
        if did == 0:
            did = 1
        donor_id = donor+"-"+str(did)
        data = donor_id+"#"+donor+"#"+address+"#"+contact+"#"+blood_group+"#"+condition+"#"+organs+"#"+aadhar+"#"+hospital+"#"+str(today)+"#Pending\n"
        saveDataBlockChain(data,"donor")
        donor_message = f"Hello {donor}, your donor ID is {donor_id}. Thank you for your donation!"
        send_sms(contact, donor_message)  # sending sms
        context= {'data':'Donor Details Added with ID : '+donor_id+"<br/>Use above Donor Id for login"}
        return render(request, 'AddDonorHistory.html', context)



def AddDonorHistory(request):
    if request.method == 'GET':
       return render(request, 'AddDonorHistory.html', {})    
    
def AddPatientHistoryAction(request):
    if request.method == 'POST':
        global hospital
        patient = request.POST.get('t1', False)
        address = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        disease = request.POST.get('t4', False)
        organs = request.POST.get('t5', False)
        aadhar = request.POST.get('t6', False)
        blood_group = request.POST.get('t7',False)
        today = date.today()
        readDetails("patient")
        rows = details.split("\n")
        if any(aadhar in row for row in rows):
            message = "Aadhar number already exists, Please try with new aadhar number."
            context = {'data': message}
            return render(request, 'AddPatientHistory.html', context)
        
        # if check_contact_exists(contact, "donor"):
        #     message = "Contact number already exists, Please try a new contact number."
        #     context = {'data': message}
        #     return render(request, 'AddPatientHistory.html', context)
        
        pid = len(rows)
        if pid == 0:
            pid = 1
        patient_id = patient+"-"+str(pid)
        data = patient_id+"#"+patient+"#"+address+"#"+contact+"#"+blood_group+"#"+disease+"#"+organs+"#"+aadhar+"#"+hospital+"#"+str(today)+"#Pending\n"
        saveDataBlockChain(data,"patient")
        patient_message = f"Hello {patient}, your patient ID is {patient_id}. We will keep you updated on your treatment!"
        send_sms(contact,patient_message) #sending sms
        context= {'data':'Patient Details Added with ID : '+patient_id+"<br/>Use above Patient Id for login"}
        return render(request, 'AddPatientHistory.html', context)

def AddPatientHistory(request):
    if request.method == 'GET':
       return render(request, 'AddPatientHistory.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def HospitalLogin(request):
    if request.method == 'GET':
       return render(request, 'HospitalLogin.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def DonorLogin(request):
    if request.method == 'GET':
       return render(request, 'DonorLogin.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})    

def checkUser(username):
    flag = False
    readDetails("signup")
    rows = details.split("\n")
    for i in range(len(rows)-1):
        arr = rows[i].split("#")
        if arr[0] == username:
            flag = True
            break
    return flag

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        hospital = request.POST.get('hospital', False)
        if checkUser(username) == False:
            data = username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+hospital+"\n"
            saveDataBlockChain(data,"signup")    
            context= {'data':'Signup Process Completed'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':'Given username already exists'}
            return render(request, 'Register.html', context)

def HospitalLoginAction(request):
    if request.method == 'POST':
        global user, hospital
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username and arr[1] == password:                
                status = 'success'
                hospital = arr[5]
                user = username
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "HospitalScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'HospitalLogin.html', context)
        

def DonorLoginAction(request):
    if request.method == 'POST':
        global user
        username = request.POST.get('username', False)
        readDetails("donor")
        rows = details.split("\n")
        status = "none"
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:                
                status = 'success'
                user = username
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "DonorScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'DonorLogin.html', context)
        
def UserLoginAction(request):
    if request.method == 'POST':
        global user
        username = request.POST.get('username', False)
        readDetails("patient")
        rows = details.split("\n")
        status = "none"
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:                
                status = 'success'
                user = username
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "UserScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'UserLogin.html', context)

