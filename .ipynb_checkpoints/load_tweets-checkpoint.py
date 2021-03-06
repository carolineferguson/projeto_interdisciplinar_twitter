from rauth import OAuth1Service
import mysql.connector
import json
import time
from pathlib import Path  
from dotenv import load_dotenv
import os
import datetime
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Autenticação com a API
try:
    read_input = raw_input
except NameError:
    read_input = input    


twitter = OAuth1Service (
    name = 'twitter',
    consumer_key =  os.getenv("consumer_key"),
    consumer_secret = os.getenv('consumer_secret'),
    request_token_url='https://api.twitter.com/oauth/request_token', 
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize', 
    base_url='https://api.twitter.com/1.1/' 
)

request_token, request_token_secret = twitter.get_request_token()

authorize_url = twitter.get_authorize_url(request_token)

print("Cole link: {url}".format(url=authorize_url))

pin = read_input('Digite o PIN')

session = twitter.get_auth_session(request_token,request_token_secret,method='POST',data={'oauth_verifier':pin})

try:
    cnx = mysql.connector.connect(user=os.getenv('user'), password=os.getenv('password'),
                              host=os.getenv('host'),port=os.getenv('port'),
                              database = os.getenv('database'))

    cursor = cnx.cursor()

except Exception as e:
    print(e)

def tweet(id,text,data,retweet,favorite,keyword):
    add_tweet = "INSERT INTO tweet (idTweetApi,textTweet,dataTweet,retweetTweet,favoriteTweet,keyword) VALUES (%s,%s,%s,%s,%s,%s)"
    params = (id,text,data,retweet,favorite,keyword)
    cursor.execute(add_tweet,params)
    cnx.commit()

def user(id,name,location):
    add_user = "INSERT INTO user (idUserTwitter,nameUser,locationUser) VALUES (%s, %s, %s)"
    params = (id,name,location)
    cursor.execute(add_user,params)
    cnx.commit()

def format_data(data):
    if(data.split()[1] == 'Jan'):
        mo = 1
    elif(data.split()[1] == 'Feb'):
        mo = 2
    elif(data.split()[1] == 'Mar'):
        mo = 3
    elif(data.split()[1] == 'Apr'):
        mo = 4
    elif(data.split()[1] == 'May'):
        mo = 5
    elif(data.split()[1] == 'Jun'):
        mo = 6
    elif(data.split()[1] == 'Jul')   :
        mo = 7
    elif(data.split()[1] == 'Aug'):
        mo = 8
    elif(data.split()[1] == 'Sep'):
        mo = 9
    elif(data.split()[1] == 'Oct'):
        mo = 10
    elif(data.split()[1] == 'Nov'):
        mo = 11
    elif(data.split()[1] == 'Dec'):
        mo = 12
    d = int(data.split()[2])
    y = int(data.split()[5])
    h = int(data.split()[3].split(sep=':')[0])
    m = int(data.split()[3].split(sep=':')[1])
    s = int(data.split()[3].split(sep=':')[2])
    return datetime.datetime(y,mo,d,h,m,s,0)

def user_twitter (id_tweet,id_user):
    cursor.execute("INSERT INTO TweetUser (tweet_idTweet, user_idUser) VALUES (%s,%s)",(id_tweet,id_user))
    cnx.commit()

def merge_user(id_user_twitter):
    cursor.execute("SELECT idUserTwitter FROM user")
    resultado = cursor.fetchall()
    for i in resultado:
        if i[0] == id_user_twitter:
            cursor.execute("SELECT idUser FROM user WHERE idUserTwitter = %s",(id_user_twitter,))
            id_user = cursor.fetchall()
            return id_user[0][0]

def merge_tweet(id_tweet_twitter):
    cursor.execute("SELECT idTweetApi FROM tweet")
    resultado = cursor.fetchall()
    for i in resultado:
        if i[0] == id_tweet_twitter:
            cursor.execute("SELECT idTweet FROM tweet WHERE idTweetApi = %s",(id_tweet_twitter,))
            id_tweet = cursor.fetchall()
            return id_tweet[0][0]

def insert_api(keyword):
    params = {'q':keyword,'lang':'pt','locale':'br','result_type': 'mixed'
             }

    r = session.get('search/tweets.json',params=params, verify=True)

    for i, tweets in enumerate(r.json()['statuses'],1):
        tweet_id = tweets['id']
        data_hora = tweets['created_at'],
        user_name = tweets['user']['screen_name']
        user_id = tweets['user']['id']
        rt = tweets['retweet_count']
        fav = tweets['favorite_count']
        text = tweets['text']
        data = format_data(data_hora[0])
        location = tweets['user']['location']



        id_tweet = merge_tweet(tweet_id)
        if id_tweet is None:
            tweet(tweet_id,text,data,rt,fav,keyword)
            id_tweet = cursor.lastrowid

        id_user = merge_user(user_id)
        if id_user is None:
            user(user_id,user_name,location)
            id_user = cursor.lastrowid

        user_twitter(id_tweet,id_user)

lista_busca = ['lockdown','quarentena','isolamento','homeoffice','covid','corona','coronavirus','vacina']

try:
    for i in lista_busca:
        insert_api(i)
        time.sleep(30)

except Exception as e:
    print(e)

else:
    print('Inserção feita')


