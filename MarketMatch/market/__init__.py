from flask import Flask, session
from flask_bcrypt import Bcrypt

# from flask_login import LoginManager
import time
import boto3
from boto3.session import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from botocore.exceptions import ClientError
import random
import datetime
import json
# from flask_dynamo import Dynamo
import os





import boto3
import credentials as keys
# from flask_wtf.csrf import CSRFProtect
from flask import Flask, current_app
# import credentials as keys




'''
Hwo to create secreat key:  security layer
 open cmd  oabd connect to python shell
    type:
    1. python
    2. import os
    3. os.urandom(12).hex()

    copy the object key

'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '429301e74ee74a46a6008982'
app.config['AWS_METADATA_SERVICE_TIMEOUT'] = 99999
app.config['AWS_METADATA_SERVICE_NUM_ATTEMPTS'] = 9999

# '8ebc857275f6a0807df07c8c'
app.config['AWS_ACCESS_KEY_ID'] = keys.AWS_ACCESS_KEY_ID
app.config['AWS_SECRET_ACCESS_KEY'] = keys.AWS_SECRET_ACCESS_KEY



session = boto3.Session( aws_access_key_id=keys.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=keys.AWS_SECRET_ACCESS_KEY, 
                        region_name= 'us-east-2')
                        
AWS_METADATA_SERVICE_TIMEOUT = 99999
AWS_METADATA_SERVICE_NUM_ATTEMPTS =99999

dynamodb = session.resource('dynamodb')
# autorefresh_session = boto3.session.Session(botocore_session=session)

# dynamodb = autorefresh_session.client.resource('dynamodb')

bcrypt = Bcrypt(app)



            
            
# login_manager = LoginManager(app)
from market import routes
from market import queries_bids



