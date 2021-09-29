from random import randint
import os
import logging
import datetime
from datetime import datetime, timedelta


def random_phone_generator():
    """
    Generate random phone number
    """
    first = str(randint(100, 999))
    second = str(randint(1, 888)).zfill(3)
    last = (str(randint(1, 9998)).zfill(4))
    while last in ['1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888']:
        last = (str(randint(1, 9998)).zfill(4))
    
    return '{}-{}-{}'.format(first, second, last)


def random_user_generator(fname_path, surname_path):
    """
    Generate user information
    """
    logging.info('loading fnames sample')
    with open(fname_path, "r", encoding="utf-8") as f:
        fnames = f.read()
    # list holding first names    
    ls_fnames = fnames.split()
    
    logging.info('loading surnames sample')
    with open(surname_path, "r", encoding="utf-8") as f:
        surnames = f.read()
    # list holding surnames    
    ls_surnames = surnames.split()

    fname = ls_fnames[randint(0, len(ls_fnames))]
    surname = ls_surnames[randint(0, len(ls_surnames))]
    user_name = fname + str(randint(123, 999)) + surname+'GEN'
    email = fname + '_' + surname + '@' + ('yahoo.com' if randint(123, 999)%9 == 0 else 'gmail.com')
    
    return {'user_name':user_name, 'fname':fname, 'surname':surname, 'email':email}


def random_buis_flight_generator(buis_flights_path):
    """
    Generate a random flight buisness
    """
    logging.info('loading business flights sample')
    with open(buis_flights_path, "r", encoding="utf-8") as f:
        flights = f.read()
        
    # list holding first names    
    ls_flights = flights.split()
    # generate a random flight company
    buis_flight=ls_flights[randint(1, len(ls_flights))]

    
    return {'buis_flight':buis_flight}    


