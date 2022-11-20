#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import json
import pytz
from datetime import datetime, timedelta
import requests
import urllib.parse
import xml.etree.ElementTree as ET

from selenium import webdriver

def save_lists():
  with open('lists.json', 'w') as f:
    json.dump(requests.get('https://communitywiki.org/trunk/api/v1/list/').json(), f, indent=2)

def find_tooters():
  '''
  collect a bunch of mastodon profiles from https://communitywiki.org/trunk/ project
  '''
  with open('lists.json', 'r') as f:
    lists = json.load(f)
  user_counter = {}
  for l in lists:
    print(f'running list: {l}')
    res2 = requests.get(f'https://communitywiki.org/trunk/api/v1/list/{l}')
    for a in res2.json():
      acct = a['acct']
      if acct in user_counter:
        user_counter[acct]['lists'].append(l)
        continue
      user_counter[acct] = {'lists':[l]}
      name, domain = acct.split('@')

      try:
        resp = requests.get(f'https://{domain}/users/{name}.rss')
        root = ET.ElementTree(ET.fromstring(resp.content)).getroot()   

        desc = root.find('./channel/description') 
        s_following = desc.text.split('Following')[0].split(',')[1].strip().split()[0] 
        s_followers = desc.text.split('Followers')[0].split(',')[1].strip().split()[0] 
        try:
          n_followers = int(s_followers)
        except:
          n_followers = 1000                  
        try:
          n_following = int(s_following)
        except:
          n_following = 1000

        user_counter[acct]['n_followers'] = n_followers
        user_counter[acct]['n_following'] = n_following
        
        last_post = pytz.utc.localize(datetime.now() - timedelta(days=30))
        recent_post = False
        last_post_text = ''
        # walk through feed for new posts
        for item in root.findall('./channel/item'):
          data = {} 
          for child in item: 
            if child.tag == 'pubDate': 
              pubdate = datetime.strptime(child.text[:-6], '%a, %d %b %Y %H:%M:%S')
              if pytz.utc.localize(pubdate) > last_post:
                recent_post = True
                last_post = pytz.utc.localize(pubdate)
            elif child.tag == 'description':
              last_post_text = child.text
          if recent_post:
            break
        
        user_counter[acct]['recent_post'] = recent_post
        user_counter[acct]['last_post'] = last_post_text
      except:
        pass
    with open('tooters.json', 'w') as file_tooters:
      json.dump(user_counter, file_tooters, indent=2, sort_keys=True)


def follow_tooters():
  with open('setup.json', 'r') as f:
    setup = json.load(f)
    
  driver = webdriver.Chrome(executable_path=setup['webdriver_location'])   
  driver.get(f'{setup["home_domain"]}/auth/sign_in')
  signin = input('type "y" once youve signed in: ')

  if signin!='y':
    return
  with open('tooters.json', 'r') as f:
    user_counter = json.load(f)
  
  for k, v in sorted(user_counter.items(), key=lambda item: len(item[1]['lists']), reverse=True):
    if ('recent_post' in v) and ('n_followers' in v) and ('n_following' in v) and v['recent_post'] and (v['n_followers'] <= setup['MAX_N_FOLLOWERS']) and (v['n_followers'] >= setup['MIN_N_FOLLOWERS']) and  (v['n_following'] / v['n_followers'] >= setup['MIN_FOLLOWING_OVER_FOLLOWER_RATIO'] ):
      name, domain = k.split('@')
      uri = urllib.parse.quote(f'https://{domain}/users/{name}', safe='')
      target = f'{setup["home_domain"]}/authorize_interaction?uri={uri}'
      driver.get(target)
      try:
        submit = driver.find_element("xpath", '/html/body/div[2]/div/form/button')
        print(f"""
          {name}
          {v['lists']}
          """)
        follow = input('follow? (press y for yes)')
        if follow=='y':
          submit.click()
      except:
        pass
    
if __name__ == '__main__':
  if len(sys.argv)!=2:
    print('1 parameter only. options: save_lists, find_tooters, follow_tooters')
    sys.exit(1)
  if sys.argv[1]=='save_lists':
    save_lists()
  elif sys.argv[1]=='find_tooters':
    find_tooters()
  elif sys.argv[1]=='follow_tooters':
    follow_tooters()
  else:
    print('input param not supported. options: save_lists, find_tooters, follow_tooters')
    sys.exit(1)
