import mysql.connector
import mysql.connector as mysql
import json
import tweepy
import time
from datetime import datetime
from time import sleep
import os
import sys
from json import loads
from flask import Flask, render_template,request,session
from flask_jsonpify import jsonpify
#from werkzeug import check_password_hash
app = Flask(__name__)

# enter your server IP address/domain name
HOST = "redmindtechnologies.com" # or "domain.com"
# database name, if you want just to connect to MySQL server, leave it empty
DATABASE = "u852023448_twitter_bot"
# this is the user you create
USER = "u852023448_twitter_bot"
# user password
PASSWORD = "Admin123$"

consumer_key ='eat3Qb7BDuOowxzCDgIp5dTfa'
consumer_secret = '1DHgcDoa4EE6Z3K7Awuaq06LgvgjFfRD21Z0ZYNIqRkHDpy47f'
access_token = '1341298822954151937-UN8peF5M0cb3mzQmtRQC6TytI9nuHo'
access_token_secret = 'UhgEDeMpiyZrLQgk89PBI9rFhStePzokMpmuglybvPaJg'


@app.route('/config', methods=['GET', 'POST'])
def configure():

        try:
            consumer_key=str(request.args.get('Consumer_key'))
            consumer_secret=str(request.args.get('Consumer_secret'))
            access_token=str(request.args.get('Access_token'))
            access_token_secret=str(request.args.get('Access_token_secret'))
            Scheduler=str(request.args.get('Scheduler'))
            status=str(request.args.get('status'))

            if(len(consumer_key)!=0 and len(consumer_secret)!=0 and len(access_token)!=0 and len(access_token_secret)!=0 and len(Scheduler)!=0 and len(status)!=0 ):
                db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
                print("Connected to:", db_connection.get_server_info())
                mycursor = db_connection.cursor()
                sql = "INSERT INTO configuration_table (consumerkey, consumersecret,accesstoken,accesstokensecret,scheduletime,status) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (consumer_key,consumer_secret,access_token,access_token_secret,Scheduler,status)
                mycursor.execute(sql, val)
                db_connection.commit()
                print(mycursor.rowcount, "record updated.")
                return jsonpify("OK")
            else:
                return jsonpify("please provide valid details")

        except mysql.Error as err:
            print(err)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return jsonpify(err)






# Authenticate to Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
# Create API object
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
user=api.me()
tweets=api.home_timeline(tweet_mode='extended')
print(user.name)

now = datetime.now()
print(now)
dt_string = now.strftime('%Y/%m/%d %H:%M:%S')
print(dt_string)

@app.route('/my-link/', methods=['GET', 'POST'])
def main():
    try:
       db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
       print("Connected to:", db_connection.get_server_info())
       mycursor = db_connection.cursor()
       tr="""select tweet_bot_id,hashtag_info_id,message,status,createddate_time,type from hashtag_info""";
       username=''
       mycursor.execute(tr)
       username=mycursor.fetchall()
       #print (username)
       results=jsonpify(username)
       print(results)
       return results

    except mysql.Error as err:
         print(err)
         #print("Error Code:", err.errno)
         print("SQLSTATE", err.sqlstate)
         print("Message", err.msg)

@app.route("/trigger", methods=['GET', 'POST'])
def saveandtrigger():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            sql = "INSERT INTO hashtag_info (hashtag_info_id, message,createddate_time,type) VALUES (%s, %s, %s, %s)"
            val = (hastagvalue,Replyvalue,dt_string,tag)
            mycursor.execute(sql, val)
            db_connection.commit()
            print(mycursor.rowcount, "record inserted.")
            #hashtag='#'+(request.args.get('hashtag'))
            #print(hashtag)
            search=(hastagvalue)
            numberoftweets=1000
            for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                print(tweet.user.name)
                api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
                #sleep(15)
            return jsonpify("OK")
        else:
            return jsonpify("please enter valid")

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)


@app.route("/save", methods=['GET', 'POST'])
def insert():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            sql = "INSERT INTO hashtag_info (hashtag_info_id, message,createddate_time,type) VALUES (%s, %s, %s, %s)"
            val = (hastagvalue,Replyvalue,dt_string,tag)
            mycursor.execute(sql, val)
            db_connection.commit()
            print(mycursor.rowcount, "record inserted.")
            return jsonpify("OK")
        else:
            return jsonpify("please enter valid")

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)

@app.route('/tweet', methods=['GET', 'POST'])
def reply():
    hashtag=(request.args.get('hashtag'))
    message=request.args.get('msg')
    print(hashtag)
    search=(hashtag)
    numberoftweets=1000
    for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
        print(tweet.user.name)
        api.update_status(status = message, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
        #sleep(15)

    return jsonpify("ok")


@app.route('/dailytweet', methods=['GET', 'POST'])
def dailytweet():
    q=[]
    hashtag=(request.args.get('hash'))
    search=(hashtag)
    numberoftweets=1000
    for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
            print(tweet.id)
            print('Nameid=',tweet.user.screen_name)
            print('Name=',tweet.user.name)
            user1=api.followers(tweet.user.name)
            a=0
            for u in user1:
                #print(u.followers_count)
                a=a+1
            print('Followers=',a)
            print('Location=',tweet.user.location)
            print('description=',tweet.user.description)
            print('tweetcount=',tweet.user.statuses_count)
            print('Verified account=',tweet.user.verified)
            print('Joined=',tweet.user.created_at)
            print('Tweeted at',tweet.created_at)
            print('Tweet Text',tweet.text)
            q.append({'Name':str(tweet.user.name),'Nameid':str(tweet.user.screen_name),'Followers':str(a), 'Location':str(tweet.user.location),'description':str(tweet.user.description),'tweetcount':str(tweet.user.statuses_count),'Verifiedaccount':str(tweet.user.verified),'Tweetedat':str(tweet.created_at),'TweetText':str(tweet.text)})
            #api.update_status("my update", in_reply_to_status_id = 1341420608437977088)
            #api.update_status(status = 'my tweety', in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
            #sleep(45)
            #api.update_status("@" + tweet.user.screen_name  +  "Test  from Tweepy Python", 1341420608437977088)
    print (json.dumps(q))
    return jsonpify(json.dumps(q))


@app.route('/trends', methods=['GET', 'POST'])
def trends():
    activetrends=[]
    trends_result = api.trends_place(2295424)
    for trend in trends_result[0]["trends"]:
        print(json.dumps(trend["name"]))
        activetrends.append({'Trend':str(trend["name"])})

    return jsonpify(json.dumps(activetrends))

@app.route("/edit", methods=['GET', 'POST'])
def editsave():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        id=(request.args.get('id'))

        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 and len(id)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            #sql = "UPDATE hashtag_info SET hashtag_info_id="+hastagvalue+" WHERE tweet_bot_id="+ id
            mycursor.execute("""
   UPDATE hashtag_info
   SET hashtag_info_id=%s, message=%s, type=%s
   WHERE tweet_bot_id=%s
""", (hastagvalue, Replyvalue, tag, id))
            db_connection.commit()
            print(mycursor.rowcount, "record updated.")
            return jsonpify("OK")
        else:
            return jsonpify("please provide valid details")

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)

@app.route("/editandtrigger", methods=['GET', 'POST'])
def editsaveandtrigger():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        id=(request.args.get('id'))

        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 and len(id)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            #sql = "UPDATE hashtag_info SET hashtag_info_id="+hastagvalue+" WHERE tweet_bot_id="+ id
            mycursor.execute("""
   UPDATE hashtag_info
   SET hashtag_info_id=%s, message=%s, type=%s
   WHERE tweet_bot_id=%s
""", (hastagvalue, Replyvalue, tag, id))
            db_connection.commit()
            print(mycursor.rowcount, "record updated.")
            search=(hastagvalue)
            numberoftweets=1000
            for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                print(tweet.user.name)
                api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
                #sleep(15)
            return jsonpify("OK")
        else:
            return jsonpify("please provide valid details")

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)

@app.route("/delete", methods=['GET', 'POST'])
def deleterec():
    try:

        id=(request.args.get('id'))

        if( id!=""):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            sql = "delete from hashtag_info WHERE tweet_bot_id="+ id+""
            mycursor.execute(sql)
            db_connection.commit()
            print(mycursor.rowcount, "record deleted.")
            return jsonpify("OK")
        else:
            return jsonpify("please Provide  valid Details" )

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)

@app.route('/login', methods=['GET', 'POST'])
def login():
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
    mycursor = db_connection.cursor()
    username=str(request.args.get('username'))
    pwd=(request.args.get('password'))
    print(username)
    sql = "SELECT  pwd FROM user WHERE email="+username
    #val=str(username)
    mycursor.execute(sql)
    row = mycursor.fetchone()
    print(row)

    if row:
        if pwd==row[0]:
            return jsonpify("OK")
        else:
            return jsonpify("Error " )

@app.route("/register", methods=['GET', 'POST'])
def register():
    try:
        Name=(request.args.get('username'))
        Email=(request.args.get('email'))
        Pass=(request.args.get('password'))
        Ph=(request.args.get('ph'))
        print(Name)
        print(Email)
        print(Pass)
        print(Ph)
        if(len(Name)!=0 and len(Email)!=0 and len(Pass)!=0 and len(Ph)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            print("Connected to:", db_connection.get_server_info())
            mycursor = db_connection.cursor()
            sql = "INSERT INTO user (name, email,pwd,phone) VALUES (%s, %s, %s, %s)"
            val = (Name,Email,Pass,Ph)
            mycursor.execute(sql, val)
            db_connection.commit()
            print(mycursor.rowcount, "record inserted.")
            return jsonpify("OK")
        else:
            return jsonpify("please enter valid")

    except mysql.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        return jsonpify(err)


@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	return jsonpify({'message' : 'You successfully logged out'})



if __name__ == '__main__':
  app.run(debug=True)

