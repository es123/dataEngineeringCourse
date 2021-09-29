# https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/

import boto3
from boto3.dynamodb.conditions import Key
import decimal
import json
import pandas as pd



class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert a DynamoDB item to JSON.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        

def df_tohtml(df_to_html, html_path, html_file_name):
        """
        Export given dataframe to html file
    
        :param df_to_html: dataframe to export to html
        :param html_path: exported html path
        :param html_file_name: exported html file name
        """
        # render dataframe as html
        html_file_name_path = html_path + html_file_name + ".html"
        df_html = df_to_html.to_html()
    
        # write the df to html for better view
        with open(html_file_name_path, "w", encoding="utf-8") as f:
            f.write(df_html)
            
def append_list(list_name, element):
    """
    append given element into given list
    used in order to avoid nature behavior of appending new element into a dictonary
    
    :param list_name: list name
    :param element: element to add into given list_name param
    """    
    try:
        list_name.append(element)
    except ValueError as e:
        print('Error:', e)
        
def append_dicts(dict_name, key, value):
    """
    append given element into given dictionary
    used in order to avoid nature behavior of appending new element into a dictonary
    
    :param list_name: dictionay name
    :param element: element to add into given dict_name param
    """    
    try:
        dict_name[key] = value  
    except ValueError as e:
        print('Error:', e)


def get_trip_enrichment(region, table, pk, entity_id_begin, html_path, delimt):
    """
    append given element into given dictionary
    used in order to avoid nature behavior of appending new element into a dictonary
    
    :param region: aws region name
    :param table: dynamodb table name to retreive data from
    :param pk: dynamodb table partition key
    :param entity_id_begin: dynamodb table sort key    
    :param html_path: html output path      
    :param delimt: entity_id_begin delimator. used for extracting out the destination
    """    
    # extract destination out of entity_id
    delimt = entity_id_begin.find(delimt)
    dest = entity_id_begin[delimt+1:]

    # Creating the DynamoDB Table Resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table)

    # get dynamodb response output
    response = table.query(
      KeyConditionExpression=Key('trip').eq(pk) & Key('entity_id').begins_with(entity_id_begin)
    )
    
    output = response['Items']
    
    print(f'display all items for pk {pk} where entity_id begins with {entity_id_begin}:\n')
    
    frames = []
    ls_transits = []
    for x, trip in enumerate(output):
        trip_converted_from_dynamodb = json.dumps(trip, cls=DecimalEncoder)
        dict_trip = json.loads(trip_converted_from_dynamodb)
        dict_transits = {"transits":""}
        ls_transits = []
        # loop over trip dictionary items
        for key, value in dict_trip.items():
            if key == 'info_transits':
                for transit in value["transits"].values():
                    # append each option transits as dictionary to ls_transits list so we can extract them al later on 
                    append_list(ls_transits, {'transit': transit})
        # append each trip option related transits dictionary to dict_transits dictionary(dictionary of dictionaries)
        append_dicts(dict_transits, 'transits', ls_transits)
        
        # convert option trnsits into json
        json_object = json.dumps(dict_transits)  
        # save json as data frame
        df = pd.read_json(json_object)
    
        # convert transits dat frame to series with only related transit values
        ser_transist = pd.DataFrame(df.transits.values.tolist())['transit']
        # normalize semi-structured JSON data into a flat table
        df_transits_all = pd.json_normalize(ser_transist)
        # select specific data frame attributes
        df_transist_attributes = df_transits_all[['cat', 'name', 'org_name', 'dest_name', 'duration', 'dist_transit', 'price_unit', 'min_price_unit']]
        # append each oprtion dataframe to frames list
        append_list(frames, df_transist_attributes)
    

    # generate html file name based on trip origin and destination
    html_file_name = pk+'_'+dest
    
    # get total options data frames
    total_options = len(frames)
    # create a list with nubers from 0 to total_options which will be used as option #index number in the general dataframe
    ls_total_options = [i+1 for i in range(0, total_options)]
    
    # concatenate datafrrames options
    try:
        df_output = pd.concat(frames, keys = ls_total_options, names = ['options', None])
        
        # replace Nan values with empty string
        # df_output = df_output.fillna("").style.set_properties(**{'background-color': 'purple', 'color': 'black', 'text-align': 'center', 'font-size': '20pt'})
        df_output = df_output.fillna("").style.set_properties(**{' background-color': 'black',  'color': 'lawngreen',  'border-color': 'white', 'text-align': 'left', 'font-size': '10pt'})
        
        
        # convert all trip options - transits dataframe to html
        df_tohtml(df_output, html_path, html_file_name)
    except ValueError as e:
        print('Error:', e)
        

get_trip_enrichment(region='us-east-2', table='r2rTrips', pk='Tel Aviv', entity_id_begin='DEST#London', html_path='/home/ec2-user/environment/.c9/Tyche/html/', delimt='#')
