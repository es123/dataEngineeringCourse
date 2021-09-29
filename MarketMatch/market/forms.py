from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from wtforms.fields.html5 import DateField
import boto3
from boto3.dynamodb.conditions import Key
from flask_table import Table, Col




class RegisterForm(FlaskForm):
    def validate_user_name(self, username_to_check):
      
        dynamodb = boto3.resource('dynamodb')
        
        table = dynamodb.Table('bids')      
        
        resp = table.query(
            KeyConditionExpression=Key('user_name').eq(username_to_check.data)
        )
        try:
            if 'Items' in resp:
                output = resp['Items'][0]
                user = output['user_name']
                print('The user is:', user)
    
            if user:     # check if their is user in the db, it rais an error if it exisit
                print('*******  The user is:' ,user, 'useUsername already exists! Please try a different username')
                flash(f'The user is: useUsername already exists! {user} Please try a different username', category='danger')
                raise ValidationError('Username already exists! Please try a different username')
        except IndexError:
            print("Go to Create new User !!!!")

           
    
    user_name = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    fname = StringField(label='First Name:', validators=[Length(min=2, max=30), DataRequired()])
    lname = StringField(label='Last Name:', validators=[Length(min=2, max=30), DataRequired()])
    phone = StringField(label='Phone:', validators=[Length(min=6, max=15), DataRequired()])
    email = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    city = StringField(label='City:', validators=[Length(min=2, max=30), DataRequired()])
    address = StringField(label='Address:', validators=[Length(min=2, max=30), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=1), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')
    



class requestForm(FlaskForm):
    category =  StringField(label='category:')
    origin = StringField(label='Origin:' , validators=[Length(min=2, max=30), DataRequired()])
    destination = StringField(label='Ddestination:', validators=[Length(min=2, max=30), DataRequired()])
   
    adults = StringField(label='No of Adults:',validators=[Length(min=1, max=2), DataRequired()])
    children = StringField(label='No of Children:',validators=[Length(min=1, max=2), DataRequired()])
    from_date = DateField('From Date' , format='%Y-%m-%d')
    to_date = DateField('Start Date', format='%Y-%m-%d')
    target_price = StringField(label='Target price:',validators=[Length(min=1, max=5), DataRequired()])
  
    submit = SubmitField(label='Create Reques')
    
    
    
class LoginForm(FlaskForm):
    user_name = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')



class CreateOfferForm(FlaskForm):
    offer =  StringField(label='offer:')
    submit = SubmitField(label='MyOffer')