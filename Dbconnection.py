from flask_ngrok import run_with_ngrok
from flask_cors import CORS
import video_upload
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
#from tamil import utf8
from flask import Flask, render_template,session
from flask import  request, render_template
from flask import send_from_directory, url_for
from flask_jsonpify import jsonpify
import requests
from werkzeug.utils import get_content_type, secure_filename

app = Flask(__name__)
run_with_ngrok(app)
CORS(app)
# enter your server IP address/domain name
HOST = "redmindtechnologies.com" # or "domain.com"
# database name, if you want just to connect to MySQL server, leave it empty
DATABASE = "u852023448_twitter_bot"
# this is the user you create
USER = "u852023448_twitter_bot"
# user password
PASSWORD = "Admin123$"

# Authenticate to Twitter

consumer_key ='Gc8S1SP0hKlCCeLXdxusPPnLa'
consumer_secret = 'mmJUkd8aLlfQ6B3k3zkVWlEzpxjoa5btv3IlLsLM53weUXv9oX'
access_token = '1341298822954151937-cidlOHMUgPVgm4vpeGN4hen3TfAUti'
access_token_secret = '9WF5WIJVZ30Cp5OP2AxsKGdHt22uHAcpU4p7YI9X8R88g'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
# Create API object
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
user=api.me()
tweets=api.home_timeline(tweet_mode='extended')
#print(user.name)

now = datetime.now()
dt_string = now.strftime('%Y/%m/%d %H:%M:%S')
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER =PROJECT_HOME
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#Configuration Save to DB
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
                mycursor = db_connection.cursor()
                sql = "INSERT INTO configuration_table (consumerkey, consumersecret,accesstoken,accesstokensecret,scheduletime,status) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (consumer_key,consumer_secret,access_token,access_token_secret,Scheduler,status)
                mycursor.execute(sql, val)
                db_connection.commit()
                return jsonpify("OK")
            else:
                return jsonpify("please provide valid detail")

        except mysql.Error as err:
            print(err)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return jsonpify(err)

#View Data
@app.route('/view/', methods=['GET', 'POST'])
def view():
    try:
       id=str(request.args.get('id'))
       db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
       #print("Connected to:", db_connection.get_server_info())
       mycursor = db_connection.cursor()
       tr="""select tweet_bot_id,hashtag_info_id,message,status,type from hashtag_info where tweet_bot_id="""+id;
       mycursor.execute(tr)
       username=mycursor.fetchall()
       return jsonpify(username)

    except mysql.Error as err:
         return jsonpify(err)

#Image Preview
@app.route('/preview', methods=['GET', 'POST'])
def Preview():
    try:
       id=str(request.args.get('id'))
       db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
       #print("Connected to:", db_connection.get_server_info())
       mycursor = db_connection.cursor()
       tr="""select img from hashtag_info where tweet_bot_id="""+id;
       mycursor.execute(tr)
       #username=mycursor.fetchall()
       #for row in username:
        #print("* {Name}".format(Name=row['img_name']))
       image_name=mycursor.fetchone()[0]
        #image =  os.path.join(app.config['UPLOAD_FOLDER'], image_name)
       return str(image_name)

    except mysql.Error as err:
         return(err)
         #print("Error Code:", err.errno)
         #print("SQLSTATE", err.sqlstate)
         #print("Message", err.msg)

#Table Display data
@app.route('/my-link/', methods=['GET', 'POST'])
def main():
    try:
       db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
       #print("Connected to:", db_connection.get_server_info())
       mycursor = db_connection.cursor()
       tr="""select tweet_bot_id,hashtag_info_id,message,status,createddate_time,type from hashtag_info""";
       username=''
       mycursor.execute(tr)
       username=mycursor.fetchall()
       results=jsonpify(username)
       return results

    except mysql.Error as err:
         jsonpify(err)

#Save and Trigger
@app.route("/trigger", methods=['GET', 'POST'])
def saveandtrigger():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 ):
            if  request.files['file']:
                mycursor = db_connection.cursor()
                img = request.files['file']
                img_name = secure_filename(img.filename)
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                img.save(saved_path)
                with open(saved_path, 'rb') as file:
                   binaryData = file.read()
                sql = "INSERT INTO hashtag_info (hashtag_info_id, message,createddate_time,type,img,img_name) VALUES (%s, %s, %s, %s,%s,%s)"
                val = (hastagvalue,Replyvalue,dt_string,tag,(binaryData),img_name)
                mycursor.execute(sql, val)
                db_connection.commit()
                # #Twitter Response
                saved_path1 = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                search=(hastagvalue)
                numberoftweets=1000
                for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                    print(tweet.user.name)
                    print(tweet.user.name)
                    msg='@'+ tweet.user.screen_name + ' '+Replyvalue
                    print(msg)
                    reply=tweet.id
                    print(reply)
                    video_upload.username1(msg,reply,img_name)
                    #print(tweet.id)
                    #upload_result = api.media_upload(saved_path1)
                    #api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id , media_ids=[upload_result.media_id],auto_populate_reply_metadata=True)

            else :
                mycursor = db_connection.cursor()
                sql = "INSERT INTO hashtag_info (hashtag_info_id, message,createddate_time,type) VALUES (%s, %s, %s, %s)"
                val = (hastagvalue,Replyvalue,dt_string,tag)
                mycursor.execute(sql, val)
                db_connection.commit()
                  #Twitter Response
                search=(hastagvalue)
                numberoftweets=1000
                for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                    print(tweet.user.name)
                    msg='@'+ tweet.user.screen_name + ' '+Replyvalue
                    print(msg)
                    reply=tweet.id
                    print(reply)
                    video_upload.reply1(msg,reply)
                    #print(tweet.user.name)
                    #api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)



            return jsonpify("OK")
        else:
            return jsonpify("please enter valid Input")

    except mysql.Error as err:
        # print(err)
        # #print("Error Code:", err.errno)
        # print("SQLSTATE", err.sqlstate)
        # print("Message", err.msg)
        return jsonpify(err)

# Create and Save Twitter
@app.route("/save", methods=['GET', 'POST'])
def insert():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            if  request.files['file']:
                mycursor = db_connection.cursor()
                img = request.files['file']
                img_name = secure_filename(img.filename)
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                img.save(saved_path)
                with open(saved_path, 'rb') as file:
                    binaryData = file.read()
                sql = "INSERT INTO hashtag_info (hashtag_info_id, message,createddate_time,type,img,img_name) VALUES (%s, %s, %s, %s,%s,%s)"
                val = (hastagvalue,Replyvalue,dt_string,tag,(binaryData),img_name)
                mycursor.execute(sql, val)
            else :
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
        return jsonpify(err)
#Twitt Reply
@app.route('/tweet', methods=['GET', 'POST'])
def reply():
    hashtag=(request.args.get('hashtag'))
    message=request.args.get('msg')
    id1=request.args.get('id')
    db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
    #print("Connected to:", db_connection.get_server_info())
    mycursor = db_connection.cursor()
    tr="""select img_name from hashtag_info where tweet_bot_id="""+id1;
    mycursor.execute(tr)
    username=mycursor.fetchall()
    for row in username:
        #print("* {Name}".format(Name=row['img_name']))
        #print(row[1])
        img_name=row[0]
        #image=row[0]
        if ((img_name)!=None):
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            # with open(img_name, 'wb') as file:
            #     file.write(image)
            # print("Stored blob data into: ", saved_path, "\n")
            search=(hashtag)
            numberoftweets=1000
            for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                print(tweet.user.name)
                msg='@'+ tweet.user.screen_name + ' '+message
                print(msg)
                reply=tweet.id
                print(reply)
                video_upload.username1(msg,reply,img_name)
                #upload_result = api.media_upload(saved_path)
                #api.update_status(status = message, in_reply_to_status_id = tweet.id , media_ids=[upload_result.media_id],auto_populate_reply_metadata=True)
                #api.update_status(status = message, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
        else :
            print(hashtag)
            search=(hashtag)
            numberoftweets=1000
            for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                print(tweet.user.name)
                msg='@'+ tweet.user.screen_name + ' '+message
                print(msg)
                reply=tweet.id
                print(reply)
                video_upload.reply1(msg,reply)
                #print(tweet.user.name)
                #api.update_status(status = message, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)

    return jsonpify("ok")

#daily Tweet Display each person wise
@app.route('/dailytweet', methods=['GET', 'POST'])
def dailytweet():
    q=[]
    hashtag=(request.args.get('hash'))
    search=(hashtag)
    numberoftweets=1000
    for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
            q.append({'Name':str(tweet.user.name),'Nameid':str(tweet.user.screen_name),'Followers':str(tweet.user.followers_count), 'Location':str(tweet.user.location),'description':str(tweet.user.description),'tweetcount':str(tweet.user.statuses_count),'Verifiedaccount':str(tweet.user.verified),'Tweetedat':str(tweet.created_at),'TweetText':str(tweet.text)})
    print (json.dumps(q))
    return jsonpify(json.dumps(q))

# Get Trending Tweets
@app.route('/trends', methods=['GET', 'POST'])
def trends():
    activetrends=[]
    trends_result = api.trends_place(2295424)
    for trend in trends_result[0]["trends"]:
        activetrends.append({'Trend':str(trend["name"]),'Count':str(trend["tweet_volume"])})

    return jsonpify(json.dumps(activetrends))

#Edit and Save IN DB
@app.route("/edit", methods=['GET', 'POST'])
def editsave():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        id=(request.args.get('id'))

        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 and len(id)!=0 ):
            db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
            mycursor = db_connection.cursor()
            if  request.files['file']:
                mycursor = db_connection.cursor()
                img = request.files['file']
                img_name = secure_filename(img.filename)

                if len(img_name)!=0 :
                    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                    img.save(saved_path)
                    with open(saved_path, 'rb') as file:
                        binaryData = file.read()
                    mycursor = db_connection.cursor()
                    mycursor.execute("""
                                        UPDATE hashtag_info
                                        SET hashtag_info_id=%s, message=%s, type=%s , img=%s, img_name=%s
                                        WHERE tweet_bot_id=%s
                                        """, (hastagvalue, Replyvalue, tag, (binaryData),img_name ,id))
                    db_connection.commit()
                else :
                    mycursor = db_connection.cursor()
                    mycursor.execute("""
                                    UPDATE hashtag_info
                                    SET hashtag_info_id=%s, message=%s, type=%s
                                    WHERE tweet_bot_id=%s
                                    """, (hastagvalue, Replyvalue, tag, id ))
                    db_connection.commit()
            else :
                mycursor = db_connection.cursor()
                mycursor.execute("""
                                    UPDATE hashtag_info
                                    SET hashtag_info_id=%s, message=%s, type=%s
                                    WHERE tweet_bot_id=%s
                                    """, (hastagvalue, Replyvalue, tag, id ))
                db_connection.commit()
                print(mycursor.rowcount, "record updated.")

            return jsonpify("OK")
        else:
            return jsonpify("please provide valid details")

    except mysql.Error as err:
        # print(err)
        # #print("Error Code:", err.errno)
        # print("SQLSTATE", err.sqlstate)
        # print("Message", err.msg)
        return (err)

@app.route("/editandtrigger", methods=['GET', 'POST'])
def editsaveandtrigger():
    try:
        hastagvalue=(request.args.get('hashtag'))
        Replyvalue=(request.args.get('msg'))
        tag=(request.args.get('tag'))
        id1=(request.args.get('id'))
        print(hastagvalue)
        print(id1)
        db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
        mycursor = db_connection.cursor()
        if(len(hastagvalue)!=0 and len(Replyvalue)!=0 and len(tag)!=0 and len(id1)!=0 ):
            if request.files['file']:
                img = request.files['file']
                print(img)
                img_name = secure_filename(img.filename)
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                img.save(saved_path)
                with open(saved_path, 'rb') as file:
                    binaryData = file.read()
                mycursor.execute("""
                                UPDATE hashtag_info
                                SET hashtag_info_id=%s, message=%s, type=%s,img=%s,img_name=%s
                                WHERE tweet_bot_id=%s
                                """, (hastagvalue, Replyvalue, tag,(binaryData),img_name, id1))
                db_connection.commit()
                saved_path1 = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                search=(hastagvalue)
                numberoftweets=1000
                for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                    upload_result = api.media_upload(saved_path1)
                    print(tweet.user.name,"here1")
                    api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id ,media_ids=[upload_result.media_id_string], auto_populate_reply_metadata=True)
                    #sleep(15)

            else :
                mycursor.execute("""
                                        UPDATE hashtag_info
                                        SET hashtag_info_id=%s, message=%s, type=%s
                                        WHERE tweet_bot_id=%s
                                        """, (hastagvalue, Replyvalue, tag, id1))
                # mycursor1 = db_connection.cursor()
                # tr="""select img_name from hashtag_info where tweet_bot_id="""+id1;
                # mycursor1.execute(tr)
                # username=mycursor.fetchall()
                # for row in username:
                #     img_name=row[0]
                #     print(img_name)
                #     saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                #     search=(hastagvalue)
                #     numberoftweets=1000
                #     for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                #         upload_result = api.media_upload(saved_path)
                #         print(tweet.user.name,"here")
                #         api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id ,media_ids=[upload_result.media_id_string], auto_populate_reply_metadata=True)
                    # else :
                search=(hastagvalue)
                numberoftweets=1000
                for tweet in tweepy.Cursor(api.search,search).items(numberoftweets):
                    print(tweet.user.name,"here2")
                    api.update_status(status = Replyvalue, in_reply_to_status_id = tweet.id , auto_populate_reply_metadata=True)
                    #sleep(15)
            db_connection.commit()
            return jsonpify("OK")
        else:
            return jsonpify("please provide valid details")

    except mysql.Error as err:
        return jsonpify(err)

# Delete Record From DB
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
        # print(err)
        # print("Error Code:", err.errno)
        # print("SQLSTATE", err.sqlstate)
        # print("Message", err.msg)
        return jsonpify(err)

# Login Page Validation
@app.route('/login', methods=['GET', 'POST'])
def login():
    try :
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
    except mysql.Error as err:
        # print(err)
        # print("Error Code:", err.errno)
        # print("SQLSTATE", err.sqlstate)
        # print("Message", err.msg)
        return jsonpify(err)

#Registerion
@app.route("/register", methods=['GET', 'POST'])
def register():
    try:
        Name=(request.args.get('username'))
        Email=(request.args.get('email'))
        Pass=(request.args.get('password'))
        Ph=(request.args.get('ph'))
        # print(Name)
        # print(Email)
        # print(Pass)
        # print(Ph)
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
        # print(err)
        # print("Error Code:", err.errno)
        # print("SQLSTATE", err.sqlstate)
        # print("Message", err.msg)
        return jsonpify(err)

#Logout
@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	return jsonpify({'message' : 'You successfully logged out'})

@app.route('/getActiveRobots', methods=['GET', 'POST'])
def getActiveRobots():
    try:
       db_connection = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD,connection_timeout=60000)
       #print("Connected to:", db_connection.get_server_info())
       mycursor = db_connection.cursor()
       tr="""select count(*) from hashtag_info where status='Active' """;
       mycursor.execute(tr)
       count=mycursor.fetchall()
       #print (username)
       results=jsonpify(count)
       #print(results)
       return results

    except mysql.Error as err:
        return jsonpify("ok")

if __name__ == '__main__':
  app.run()
