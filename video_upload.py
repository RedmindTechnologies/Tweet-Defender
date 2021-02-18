import os
import sys
import time
from flask import Flask, session, redirect, url_for, request
import json
import requests
from requests_oauthlib import OAuth1



MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'


consumer_key ='ff08kr1rdRJPF95gw0J6mzIfW'
consumer_secret = 'RCTUKReT22A9UPHlkOVB2kiouY9p66oRQzpGtEw5acEva1FhOI'
access_token = '1362005227637936130-XqCR9aM8HPY4uV60Ft6Sj66Le72XS7'
access_token_secret = 'KntThVz04HVWgQhi3UCo4jSve4Xbb61Ni7oGSj40EZcWo'

VIDEO_FILENAME = 'vijay.jpg'

oauth = OAuth1(consumer_key,
  client_secret=consumer_secret,
  resource_owner_key=access_token,
  resource_owner_secret=access_token_secret)

def username1(VIDEO_Name,s,w):
  d=VIDEO_Name
  print(d)
  videoTweet = VideoTweet(w)
  videoTweet.upload_init(w)
  videoTweet.upload_append()
  videoTweet.upload_finalize()
  videoTweet.tweet1(VIDEO_Name,s)

def reply1(msg,reply):
  VideoTweet.tweet(msg,reply)




class VideoTweet(object):

  def __init__(self, file_name):
    '''
    Defines video tweet properties
    '''
    self.video_filename = file_name
    self.total_bytes = os.path.getsize(self.video_filename)
    self.media_id = None
    self.processing_info = None


  def upload_init(self,video_filename):
    '''
    Initializes Upload
    '''
    print('INIT')

    if(video_filename.find('.mp4')==-1):
      print(video_filename)
      request_data = {
        'command': 'INIT',
        'media_type': 'image/jpg',
        'total_bytes': self.total_bytes,
        'media_category': 'tweet_image'
      }
    else:
      print(video_filename)
      request_data = {
        'command': 'INIT',
        'media_type': 'video/mp4',
        'total_bytes': self.total_bytes,
        'media_category': 'tweet_video'
      }


    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    media_id = req.json()['media_id']

    self.media_id = media_id

    print('Media ID: %s' % str(media_id))


  def upload_append(self):
    '''
    Uploads media in chunks and appends to chunks uploaded
    '''
    segment_id = 0
    bytes_sent = 0
    file = open(self.video_filename, 'rb')

    while bytes_sent < self.total_bytes:
      chunk = file.read(4*1024*1024)

      print('APPEND')

      request_data = {
        'command': 'APPEND',
        'media_id': self.media_id,
        'segment_index': segment_id
      }

      files = {
        'media':chunk
      }

      req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=oauth)

      if req.status_code < 200 or req.status_code > 299:
        print(req.status_code)
        print(req.text)
        sys.exit(0)

      segment_id = segment_id + 1
      bytes_sent = file.tell()

      print('%s of %s bytes uploaded' % (str(bytes_sent), str(self.total_bytes)))

    print('Upload chunks complete.')


  def upload_finalize(self):
    '''
    Finalizes uploads and starts video processing
    '''
    print('FINALIZE')

    request_data = {
      'command': 'FINALIZE',
      'media_id': self.media_id
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    print(req.json())

    self.processing_info = req.json().get('processing_info', None)
    self.check_status()


  def check_status(self):
    '''
    Checks video processing status
    '''
    if self.processing_info is None:
      return

    state = self.processing_info['state']

    print('Media processing status is %s ' % state)

    if state == u'succeeded':
      return

    if state == u'failed':
      sys.exit(0)

    check_after_secs = self.processing_info['check_after_secs']

    print('Checking after %s seconds' % str(check_after_secs))
    time.sleep(check_after_secs)

    print('STATUS')

    request_params = {
      'command': 'STATUS',
      'media_id': self.media_id
    }

    req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)

    self.processing_info = req.json().get('processing_info', None)
    self.check_status()


  def tweet(self,msg):
    '''
    Publishes Tweet with attached video
    '''
    request_data = {
      'status': self,
      'in_reply_to_status_id' : msg,
      #'media_ids': self.media_id
    }

    req = requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)
    print(req.json())

  def tweet1(self,msg,reply):
    '''
    Publishes Tweet with attached video
    '''
    request_data = {
      'status': msg,
      'in_reply_to_status_id' : reply,
      'media_ids': self.media_id
    }

    req = requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)
    print(req.json())


if __name__ == '__main__':
  videoTweet = VideoTweet(VIDEO_FILENAME)
  videoTweet.upload_init()
  videoTweet.upload_append()
  videoTweet.upload_finalize()
  videoTweet.tweet(d)
