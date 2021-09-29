from elasticsearch import Elasticsearch
from pandasticsearch import Select
from elasticsearch.helpers import bulk
import pandas as pd
from utils import create_directories
from Notify import Notify
from dotenv import load_dotenv
import os
from datetime import datetime


# Load email account variables from .env
load_dotenv()

'''
DESCRIBE:
- load org tweets documents from elastic into a data frame
- craete a new data frame to hold only relevant columns
- delete documents 
  - without location 
  - retweets 
- loading clean tweets data frame back to elastic into tweets_antisemitic_clean index
- exporting clean df to html

TODO:

- handle count_per_day_col reports view sorting
- split cleaning_df function into separeted functions such remove_column , delete_records etc.
- in currently logic we delete elastic tweets_antisemitic_clean and reload each time.
  later on we might dev deifferncial loading
'''


class AnalyzeElastic():
    def __init__(self, elk_index):
        """
        # Class constructor / initialization method.
        # Load from elastic, cleaning data, generate reports and upload to elastic

        :param elk_index: elastic index name
        :return [datadrame] loaded df
        """
        self.es = Elasticsearch()
        self.elk_index = elk_index

    def load_elastic(self):
        """
        # Load elastic index data into a dataframe
        """
        # get index info
        index_info = self.es.search(
            index=self.elk_index,
            body={
                "query": {
                    "match_all": {}
                }
            }
        )

        # get total documents in index
        index_info_total_rows = index_info["hits"]["total"]["value"]

        # es_response_dict = es.search(index="tweets_antisemitic", body={"query": {"match_all": {}}})
        es_response_dict = self.es.search(index=self.elk_index, body={}, size=index_info_total_rows)

        # create a data frame using elastic index documents
        df = Select.from_dict(es_response_dict).to_pandas()

        return df

    def clone_df(self, org_df, clone_clomns=[], is_partialy_clone=True):
        """
        # Clone given dataframe

        :param org_df: original dataframe
        :param clone_clomns: specify dataframe columns to be cloned
        :param is_partialy_clone: specify if clonning type is fulll or partial
        :return [datadrame] cloned dataframe
        """
        self.org_df = org_df
        self.clone_clomns = clone_clomns
        self.is_partialy_clone = is_partialy_clone

        cloned_df = pd.DataFrame()

        # create a new dataframe to holds only relevant columns from the given clone_clomns
        if is_partialy_clone:
            try:
                cloned_df = pd.DataFrame(org_df[clone_clomns])
                print(f'clonning partital dataframe completed succssefully')
            except:
                print(f'error occured while trying clonning dataframe')
        # create a clone dataframe based on the given org_df
        else:
            try:
                # create a new dataframe to holds only relevant columns
                cloned_df = self.org_df
                print(f'clonning the whole dataframe into new dataframe completed succssefully')
            except:
                print(f'error occured while trying clonning the whole dataframe')
        return cloned_df

    def lower_text(self, text):
        """
        # Lower given text

        :param text: string to be lower
        :return [string] lower string
        """
        self.text = text

        text_list = [word.lower() for word in str(self.text).split()]
        text_lower = ' '.join(text_list)
        return text_lower

    def cleaning_df(self, df_to_clean):
        """
        # Cleansing given dataframe

        :param text: string to be lower
        :return [dataframe] cleaned dataframe
        """

        self.df_to_clean = df_to_clean

        # convert created_at field to datetime datatype
        self.df_to_clean['created_at'] = pd.to_datetime(self.df_to_clean['created_at'])

        # lower all status words for further analysis
        self.df_to_clean["text"] = self.df_to_clean["text"].apply(self.lower_text)

        # add Series of is_retweet for further analysis
        self.df_to_clean["is_retweet"] = ~df_to_clean['retweeted_status.created_at'].isnull()

        # add Series of is_location for further analysis
        self.df_to_clean["is_location"] = ~self.df_to_clean['location'].isnull()

        # cleaning retweeted tweets
        self.df_to_clean = self.df_to_clean.loc[self.df_to_clean["is_retweet"] == False]
        # cleaning tweets without locations
        self.df_to_clean = self.df_to_clean.loc[self.df_to_clean["is_location"] == True]

        # drop irrlevant columns
        self.df_to_clean = self.df_to_clean.drop(["is_retweet", "is_location", "retweeted_status.created_at"],
                                                 axis=1,
                                                 inplace=False)

        # map similar location values typed in tweets profile in order to allow aggregations per unique kets
        mapping = {'Shillong Meghalaya India': 'Shillong Meghalaya India',
                   'New York': 'New York',
                   'New York, USA': 'New York',
                   'New York, NY': 'New York',
                   'NYC': 'New York',
                   'Manhattan, NY': 'New York',
                   'Los Angeles, CA': 'Los Angeles',
                   'Washington, DC': 'Washington',
                   'United States': 'USA',
                   'USA': 'USA',
                   'United Kingdom': 'United Kingdom',
                   'UK': 'United Kingdom',
                   'England, United Kingdom': 'United Kingdom',
                   'London, England': 'United Kingdom',
                   'London': 'United Kingdom',
                   'Canada': 'Canada',
                   'Toronto': 'Canada',
                   'Toronto, Ontario': 'Canada',
                   'Israel': 'Israel',
                   'Amsterdam': 'Amsterdam',
                   'Planet Earth': 'Unknown',
                   'Brooklyn, NY ': 'New York',
                   'she/her   ': 'unknown',
                   'Oviedo, Florida': 'Florida',
                   'South Wales': 'Wales',
                   'Palestine 1917 - 1948 - 2021': 'Palestine',
                   'Los Angeles ': 'Los Angeles',
                   'Florida, USA': 'Florida',
                   'New Jersey ': 'New Jersey ',
                   'India': 'India',
                   'Chicago, IL': 'Chicago',
                   'Australia': 'Australia',
                   'California': 'California',
                   'Dublin City, Ireland': 'Dublin',
                   'The United States of America': 'USA',
                   'Toronto, Canada': 'Canada',
                   'Iraq': 'Iraq',
                   'on a mountain north of gotham': 'Unknown',
                   'Myrtle Beach S.C': 'Unknown',
                   'Texas, USA ': 'USA',
                   'Chicago': 'Chicago',
                   'Boston, MA ': 'Boston',
                   'Philadelphia, PA': 'Philadelphia',
                   'San Francisco, CA': 'San Francisco',
                   'Uk': 'United Kingdom',
                   'San Francisco ': 'San Francisco',
                   'Chapel Hill, NC': 'North Carolina',
                   'My body; currently on Earth': 'Unknown',
                   'the old pueblo': 'Unknown',
                   'California, USA': 'USA'
                   }
        # map similar locations for furthur analysis
        self.df_to_clean['location_tuned'] = self.df_to_clean['location'].apply(lambda x: mapping[x] if x in mapping.keys() else None)

        # delete rows in case one of the column is None
        self.df_to_clean = self.df_to_clean.dropna()

        return self.df_to_clean

    def upload_elastic(self, df_upload_elastic, elk_upload_index):
        """
        # Convert given datframento list of dictionaries and upload it into elastic index

        :param df_upload_elastic: string to be lower
        :param elk_upload_index: string to be lower
        """
        self.df_upload_elastic = df_upload_elastic
        self.elk_upload_index = elk_upload_index

        # convert dataframe to list of dictionaries
        ls_clean_tweets = self.df_upload_elastic.to_dict(orient='records')

        # delete the tweets_antisemitic_clean index from elastic if exists
        if self.es.indices.exists(index=self.elk_upload_index):
            self.es.indices.delete(index=self.elk_upload_index)

        # create the tweets_antisemitic_clean index in elastic if not exists
        if not self.es.indices.exists(index=self.elk_upload_index):
            self.es.indices.create(index=self.elk_upload_index, body={})

        # load bulk data into elastic
        bulk(self.es, ls_clean_tweets, index=self.elk_upload_index, raise_on_error=True)

    def df_tohtml(self, df_to_html, df_to_html_path, df_to_html_name):
        """
        # Export given dataframe to html file

        :param df_to_html: dataframe to export to html
        :param df_to_html_path: exported html path
        :param df_to_html_name: exported html file name
        """
        # render dataframe as html
        self.df_to_html = df_to_html
        df_html = self.df_to_html.to_html()

        # write the df to html for better view
        with open(df_to_html_path + df_to_html_name + ".html", "w", encoding="utf-8") as f:
            f.write(df_html)

    def generate_report(self, rp_type, df_to_rp, df_agg_col=None, rp_html_path=None, rp_html_name=None, head=20):
        """
        # Generate dataframe report based on given dataframe plus option to export it to html file

        :param rp_type: report file
        :param df_to_rp: source dataframe
        :param df_agg_col: aggregation column
        :param rp_html_path: html report path
        :param rp_html_name: html file name
        :param head: top rows to be exported to html file
        :return [dataframe] dataframe report
        """
        self.rp_type = rp_type
        self.df_to_rp = df_to_rp
        self.df_agg_col = df_agg_col
        self.rp_html_path = rp_html_path
        self.head = head

        # display total tweets
        if rp_type == 'info':
            locs = df_to_rp[df_agg_col].value_counts()
            print(f'Total tweets this period:', len(self.df_to_rp.index), '\n')
            print('Total counries with 5 and more tweets:', locs[locs >= 5].count())
            print('Counries with 5 and more tweets:\n',locs[locs>=5])

        # generate tweets per day and given column report
        if rp_type == 'count_per_day_col':
            if self.df_agg_col:
                ser_group_day_col = self.df_to_rp.set_index('created_at').groupby(self.df_agg_col)["id"].resample("D").count()
                df_count_day_col = ser_group_day_col.to_frame()
                df_count_day_col.sort_values(by=['id', 'created_at'], ascending=False)
                df_count_day_col.head(head)
            if rp_html_path:
                self.df_tohtml(df_count_day_col, rp_html_path, rp_html_name+'_'+self.df_agg_col)
            return df_count_day_col

        # generate tweets per given column report
        if rp_type == 'count_per_col':
            if self.df_agg_col:
                # add df_agg_col and id to the new df
                # grouping by given df_agg_col and count id
                # reset index
                # sort values by by the agg function column
                # display first 20 rows
                df_count_per_col = self.df_to_rp[[self.df_agg_col, 'id']] \
                .groupby([self.df_agg_col])['id'].count() \
                .reset_index(name='Total') \
                .sort_values(['Total'], ascending=False) \
                .head(self.head)

                # reset index to be ordered by the agg function column
                df_count_per_col.reset_index(drop=True, inplace=True)
                # add 1 to each index so the counting will start from 1
                df_count_per_col.index = df_count_per_col.index + 1

            if rp_html_path:
                self.df_tohtml(df_count_per_col, rp_html_path, rp_html_name+'_'+self.df_agg_col)

            return df_count_per_col


def main():
    #######  set reports path #######

    df_reports_path = r'.\reports\dataframes\\'
    kibana_reports_path = r'.\reports\kibana\\'

    #######  create directories #######

    create_directories(df_reports_path)
    create_directories(kibana_reports_path)

    #######  load elastic raw data, clean and upload back and generate clean data report #######

    # load from elastic
    tweetsAnalyze = AnalyzeElastic('tweets_antisemitic')

    es_df = tweetsAnalyze.load_elastic()
    # clone specific columns to a new dataframe
    cloned_df = tweetsAnalyze.clone_df(es_df, ["id", "created_at", "name", "text", "location", "followers_count",
                                               "friends_count", "retweeted_status.created_at"])

    # delete empty location
    # aggregate locations values using mapping dictionary built manually
    # based on more then 4 tweets per location
    df_clean_tweets = tweetsAnalyze.cleaning_df(cloned_df)

    #######  generates reports  #######

    # export dataframe to html
    tweetsAnalyze.df_tohtml(df_clean_tweets, df_reports_path, "clean_tweets")

    # return high level stats per given dataframe
    print('~'*50, 'cloning dataframe from elastic info', '~'*50)
    tweetsAnalyze.generate_report('info', es_df, 'location')
    print('~'*60, 'clean dataframe info', '~'*60)

    tweetsAnalyze.generate_report('info', df_clean_tweets, 'location_tuned')
    # generate reports per user
    tweetsAnalyze.generate_report('count_per_col', df_clean_tweets, 'name', df_reports_path, "total_tweets", 15)
    # generate reports per location
    df_total_location = tweetsAnalyze.generate_report('count_per_col', df_clean_tweets, 'location_tuned', df_reports_path, "total_tweets", 20)

    # generate reports per day per location
    tweetsAnalyze.generate_report('count_per_day_col', df_clean_tweets, 'location_tuned', df_reports_path, "total_tweets_per_day")
    # generate reports per day per user
    tweetsAnalyze.generate_report('count_per_day_col', df_clean_tweets, 'name', df_reports_path, "total_tweets_per_day")

     #######  send notifications  #######

    # get max tweets per user
    max_tweets = df_total_location["Total"]
    max_tweets_val = max_tweets.max()
    # define treshold to send notification
    max_tweets_tresh = 5

    #######  upload df to elstic in bulk  #######
    tweetsAnalyze.upload_elastic(df_clean_tweets, 'tweets_antisemitic_clean')

    #######  notify user in case max tweets treshold was reached  #######
    notify_by_email = True

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if notify_by_email and max_tweets_val > max_tweets_tresh:
        sender = 'eransamail@gmail.com'
        # extracted from .env file
        pwd = os.getenv('ACCOUNT_PWD')
        recipients = ["eransamail@gmail.com", "esaddress@gmail.com"]
        subj = "Unusual tweets Alarm"
        body = "Pay attention, unusual tweets were sent recently !!! \n" + "see below report related to " + current_time
        attachments = r".\reports\dataframes\total_tweets_location_tuned.html"

        notify_user = Notify()
        notify_user.send_notification(sender, pwd, recipients, subj, body, attachments)

if __name__ == "__main__":
    # calling main function
    main()









