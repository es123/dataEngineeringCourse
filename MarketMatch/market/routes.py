from market import app
from flask import render_template, redirect, url_for, flash
# from market.models import Item, User  # imherit /ipmport the methot user and item from models.py
from market.forms import RegisterForm, LoginForm , requestForm ,CreateOfferForm # we create a package -- market

# from flask_login import login_user,logout_user, login_required
from os import listdir
import json

# request is a part of Flask's HTTP requests
from flask import request
import datetime
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os
from flask import Flask

import credentials as keys
from flask import Flask, session
from flask_table import Table, Col
import decimal
from market import queries_bids as qry
import re
import sys
import uuid
import logging

#now we will Create and configure logger 
logging.basicConfig(filename="log_file.log", 
					format='%(asctime)s %(message)s', 
					filemode='w') 

#Let us Create an object 
logger=logging.getLogger() 

#Now we are going to Set the threshold of logger to DEBUG 
# logger.setLevel(logging.DEBUG) 





def flatten_dict(dd, separator='_', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
       

        
    form = LoginForm()
    
    if request.method =='POST':
        user = form.user_name.data 
        session["user"] = user

     
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('bids')    
    if form.validate_on_submit():
    
    
        try:
            
            user_name =  form.user_name.data
            password = form.password.data
            print (user_name)
           
            table = dynamodb.Table('bids')
           
            response = table.get_item(  Key={
                'user_name': form.user_name.data,
                'entity_id': 'CUST#' +  form.user_name.data
            }
            )
        
            
            
            item = response['Item']
            print(item)
            attempted_user = item['user_name']
            print(attempted_user)
            if password == item['password']:
                # login_user(attempted_user)
                flash(f'Success! You are logged in as: {attempted_user}', category='success')
                logger.info("User Login successfully ")
                return redirect(url_for("user"))
       
            else:
                flash('The password Or UserName is not Correcr', category='danger')
                if "user" in session:
                  	return redirect(url_for("user"))
                
        except IndexError:
            flash('The password Or UserName is not Correcrt ', category='danger')
            return redirect(url_for('login_page'))
        except:
            flash('Something  went wrong - check  UserName is not Correcrt ', category='danger')
            logger.error("Unexpected error - Login  - check user exsist ")
            print("Unexpected error:", sys.exc_info()[0])
            return redirect(url_for('login_page'))
            
  
   
    return render_template('login.html', form=form)
        
   

@app.route('/register', methods=['GET', 'POST'])



def register_page():
    form = RegisterForm()
    if request.method =='POST':
        user = form.user_name.data 
        session["user"] = user
    
    
    if form.validate_on_submit():
        
        
        
        item = {
                  'user_name': form.user_name.data,
                  'entity_id': 'CUST#'+ form.user_name.data,
                  'create_date': datetime.datetime.utcnow().isoformat(),
                  'update_date': datetime.datetime.utcnow().isoformat(),
                            
                  'fname':form.fname.data,
                  'lname':form.lname.data,
                  'timestamp': datetime.datetime.utcnow().isoformat(),
                    
                  'password':form.password1.data,
                  'cust_contact': {"phone":form.phone.data,"email":form.email.data,"city": form.city.data,"address":form.address.data}
                }

          
        try:    
            kinesis_client = boto3.session.Session().client('kinesis')
        
            raw_data = json.dumps(item)
            encoded_data = bytes(raw_data, 'utf-8')
            kinesis_record = {
                'Data': encoded_data,
                'PartitionKey': item['user_name'],
            }
            
            
            kinesis_record_list = []
            kinesis_record_list.append(kinesis_record)
            print(kinesis_record_list)
            
            req = {
                        'Records': kinesis_record_list,
                        'StreamName': 'stream_bids_kinesis_dynamodb'
                    }
            
            
            kinesis_client.put_records(**req)
            flash(f"Account created successfully! You are now logged in as { form.user_name.data}", category='success')
          
            print('@'*5, 'finish create user with kinesis','@'*5)
            logger.info("finish create user with kinesis ")
            return redirect(url_for("user"))
            
        except: 
            print('Something went wrong')
            print('@' * 150)
            if "user" in session:
                return redirect(url_for("user"))
      
            
    return render_template('register.html', form=form)

   
@app.route('/create_request',  methods=['GET', 'POST'])
 

def create_request_page():
    if "user" in session:
        
        user = session["user"]
        print("user is:", user)
        # return f"<h1>{user}</h1>"
       
    else:
        return redirect(url_for('login_page'))
    
    
     
    # /***************/
    
    TABLE_NAME = "bids"

    # Creating the DynamoDB Client
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")
    
    # Creating the DynamoDB Table Resource
    dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
    table = dynamodb.Table(TABLE_NAME)

   
    response = table.query(
    KeyConditionExpression=Key('user_name').eq(user) & Key('entity_id').begins_with('BID#')
    )

    output = response['Items']
    print(response['Items'])

    

    bid_output = []
 
    for i in output:
       
        d = i['bid_info']
        d['entity_id'] = i['entity_id']
        d['category'] = i['category']
        d['html_file'] ="static/InfoTransit/from_"+ d['origin']+ "_to_" + d['destination'] + ".html"
 
        # d['enrich'] = [{'max_price': int (d['target_price']) +100 ,"xxx": j },{'max_price': int (d['target_price']) +200 ,"xxx": j }]
        bid_output.append(i['bid_info'])
    
    print(bid_output)
################    
    TABLE_NAME_INFO = "r2rTrips"
    limt_output = 1
    
    # Creating the DynamoDB Client
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")
    
    # Creating the DynamoDB Table Resource
    dynamodb_b = boto3.resource('dynamodb', region_name="us-east-2")
    table_b = dynamodb_b.Table(TABLE_NAME_INFO)
    
    # Helper class to convert a DynamoDB item to JSON.
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)
    
    
    ############################ Get all Destinations for origin Delhi ##########################################
    # Use the Table resource to query all entity_id Items by specific Customer
    # that start with 'BID#'
    pk = 'Tokyo'
    entity_id_begin = 'DEST#Delhi'
    
    response_b = table_b.query(
      KeyConditionExpression=Key('trip').eq(pk) & Key('entity_id').begins_with(entity_id_begin)
    )
    
    output_b = response_b['Items']
    
    print(f'display all items for pk {pk} where entity_id begins with {entity_id_begin}:\n')
    for i, trip in enumerate(output_b):
        if i > limt_output:
          break
        trip_converted_from_dynamodb = json.dumps(trip, cls=DecimalEncoder)
        dict_trip = json.loads(trip_converted_from_dynamodb)
        for i in dict_trip.items():
            print(f'{i[0]} : {i[1]}')
   
    
    # print('a=' * 150)       
    # print(bid_output)
    # print('b=' * 150)

  
    form = requestForm()
    if "user" in session:
        
        user = session["user"]
        # print("user is:", user)

    else:
        return redirect(url_for('login_page'))
    


    form = requestForm()
 
    if form.validate_on_submit():
        try:
            
            kinesis_client = boto3.session.Session().client('kinesis')
            
            unique = uuid.uuid4().hex
            unique_bid = 'BID#'+str(unique)
            print(unique_bid)
            item = {
                
                  'user_name':  user,
                  'entity_id': unique_bid ,
                  'timestamp' :datetime.datetime.utcnow().isoformat(),
                  'create_date': datetime.datetime.utcnow().isoformat(),
                  'update_date': datetime.datetime.utcnow().isoformat(),
                  'status': 'open',               
                  'category':   form.category.data,
                  'bid_info': {"origin":  form.origin.data,
                                "destination":  form.destination.data,   
                                "adults":form.adults.data,     
                                "children":form.children.data,   
                                "from_date" : form.from_date.data.isoformat(),
                                "to_date":  form.to_date.data.isoformat(),
                                "target_price": form.target_price.data
                       
                  }
                   
            }
            
          
            print(item)
            def myconverter(o):
                    if isinstance(o, datetime.datetime):
                        return o.__str__()
                        
      
            raw_data = json.dumps(item)
            encoded_data = bytes(raw_data, 'utf-8')
            kinesis_record = {
                'Data': encoded_data,
                'PartitionKey': item['user_name'],
            }

            kinesis_record_list = []
            kinesis_record_list.append(kinesis_record)
            print(kinesis_record_list)
            
            req = {
                        'Records': kinesis_record_list,
                        'StreamName': 'stream_bids_kinesis_dynamodb'
                    }
            
            
            kinesis_client.put_records(**req)   
            print(user)

            flash(f"You create new request Successfuly !! in as   {user}", category='success')
     

        except:
            flash(f"Sommsing Worng !! in as   {user}", category='danger')
            flash(f"Unexpected error:  {sys.exc_info()[0]}", category='danger')


    return render_template('create_request.html', form=form,bid_output = bid_output)
    
    
@app.route("/user")
def user():
	if "user" in session:
		user = session["user"]
		return redirect(url_for("create_request_page"))
	else:
		return redirect(url_for("login_page"))

@app.route("/logout")
def logout():
    print("gjggdgsg")
    session.pop("user", None)
    flash(f" {user}, Thank You - You have been logged out!", category='info')
    return redirect(url_for("home_page"))



@app.route('/all_bids', methods=['GET', 'POST'])



def all_bids_page():
    if "user" in session:
        
        user = session["user"]
        print("user is:", user)

    else:
        return redirect(url_for('login_page'))
     
  
    gen_items = qry.scan_users("BID#")
    ls_items = list(gen_items)
    print('k~' *150) 
    print(gen_items)
  

    ls_bid = []
    
    for item in ls_items:
      bid_output = json.loads(item)
      ls_bid.append(flatten_dict(bid_output))
   
    bid_output = ls_bid
   
    # print('k~' *150) 
    # print(bid_output)
    # print('k~' *150) 
    
    
     
 
  
    

    
    form = CreateOfferForm()
  
    if form.validate_on_submit():
        print('HI *-**********')
    
    return render_template('all_bids.html' ,bid_output = bid_output , form=form)
    
    
@app.route('/all_my_offers', methods=['GET', 'POST'])



def all_my_offers_page():
    if "user" in session:
        
        user = session["user"]
        print("user is:", user)

    else:
        return redirect(url_for('login_page'))
     
  
    TABLE_NAME = "bids"

    # Creating the DynamoDB Client
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")
    
    dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
    table = dynamodb.Table(TABLE_NAME)


    response = table.query(
    KeyConditionExpression=Key('user_name').eq(user) & Key('entity_id').begins_with('OFFER#')
    )
 
    output = response['Items']
    print(response['Items'])
    

    ls_offer=[]

    for i in output:
    
        s = i.get('entity_id')
        try:
            user_offer = re.search('#(.*)#', s)
            user_offer = user_offer.group(1)
        except:
            user_offer = 'No User Define'
        i['user_offer'] = user_offer
        ls_offer.append(flatten_dict(i))
        s = str(type(ls_offer))
        print(s)
     

    

    
    return render_template('all_my_offers.html', ls_offer = ls_offer )


