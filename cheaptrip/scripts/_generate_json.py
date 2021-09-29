import requests
import logging

debug = 0

# origin = 'Tel-Aviv'
# dest = 'Greece'
#
# BASE_URL = 'https://www.rome2rio.com/map/'
# BASE_HTML_PATH = r'C:\Eran\DataEngineering\Project\cheaptrip\files\html\\'
# BASE_JSON_PATH = r'C:\Eran\DataEngineering\Project\cheaptrip\files\json\\'
#
# html_file_path = BASE_HTML_PATH + origin + '_' + dest + '.txt'
# json_file_path = BASE_JSON_PATH + origin + '_' + dest + '.txt'
# url = BASE_URL + origin + '/' + dest

def generate_list(url, output_html_path, output_json_path, debug=0):
    # output_html_path = base_html_path + origin + '_' + dest + '.txt'
    # if not os.path.isfile(output_json_path):
    # url = 'https://www.rome2rio.com/map/Badrinath/Zurich/'
    response = requests.get(url)

    # write url html to a file
    with open(output_html_path, 'w', encoding='utf-8') as f:
        if debug == 1:
            logging.info(f'writing to file {output_html_path}')
        f.write(response.text)

    with open(output_html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # logging.info(html)
    #
    sep = r"deeplinkTrip"
    start_info = html.find(sep)
    # logging.info(start_info)
    start_quote = html.find("='", start_info)
    # logging.info(start_quote)
    end_quote = html.find('/>', start_quote)
    # logging.info(end_quote)
    body = html[start_quote + 2: end_quote-2]
    if debug == 1:
        logging.info(body)

    # output_json_path = base_json_path + origin + '_' + dest + '.json'
    with open(output_json_path, 'w', encoding='utf-8') as f:
        if debug == 1:
            logging.info(f'writing to file {output_json_path}')
        f.write(body)

    # # logging.info(page[start_quote:end_quote])
# generate_list(BASE_URL, html_file_path, json_file_path)