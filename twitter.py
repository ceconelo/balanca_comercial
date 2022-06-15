#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tweepy
from tweepy.auth import OAuth1, OAuthHandler
from configparser import RawConfigParser
from datetime import datetime

from loguru import logger as log

from time import sleep

config_parser = RawConfigParser()
config_parser.read('settings.ini')
credentials = config_parser['credentials']

'''
    This module is responsible for requests to the twitter API through the tweetpy library.
    There are 3 main functions:
    1. Create an object with read and write permissions on twitter
    2. Search recent tweets
    3. Post new tweets in sequential mode 
'''


# Object with permissions to consume the Twitter API.
def get_client():
    # According to the library documentation we need a project created
    # on the twitter platform. In this project we get the keys and tokens needed for the connection.
    client = tweepy.Client(bearer_token=credentials['bearer_token'],
                           access_token=credentials['access_token'],
                           access_token_secret=credentials['access_token_secret'],
                           consumer_key=credentials['api_key'],
                           consumer_secret=credentials['api_key_secret'],
                           wait_on_rate_limit=False)

    auth = OAuthHandler(client.consumer_key,
                        client.consumer_secret)

    auth.set_access_token(client.access_token, client.access_token_secret)
    api = tweepy.API(auth=auth)

    return client, api


def search_tweets_user(client, query, max_results):
    """
    Returns tweets from a specific userid
    """
    start = datetime.today().strftime('%Y-%m-%dT') + '03:00:00Z'
    tweets = client.get_users_tweets(client.get_me().data.id, max_results=max_results, start_time=start)
    tweet_data = tweets.data
    results = []
    if not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            if (tweet.text.split('\n')[0] == query.split('-')[0].strip()) \
                    or (tweet.text.split('https')[0].strip() == query.split('-')[0].strip()):
                results.append({
                    'id': tweet.id,
                    'text': tweet.text
                })
    return results


def search_tweets_surface(client, query, max_results):
    """
    Searching for Tweets is an important feature used to surface Twitter conversations about a specific topic or event.
    While this functionality is present in Twitter, these endpoints provide greater flexibility and power when filtering
    for and ingesting Tweets so you can find relevant data for your research more easily; build out near-real-time
    ‘listening’ applications; or generally explore, analyze, and/or act upon Tweets related to a topic of interest.
    """
    start = datetime.today().strftime('%Y-%m-%dT') + '03:00:00Z'
    tweets = client.search_recent_tweets(query=query, max_results=max_results, start_time=start)
    tweet_data = tweets.data
    results = []
    if not tweet_data is None and len(tweet_data) > 0:
        for tweet in tweet_data:
            results.append({
                'id': tweet.id,
                'text': tweet.text
            })
    return results


def get_tweet(client, id):
    tweet = client.get_tweet(id, expansions=['author_id'], user_fields=['username'])
    return tweet


# Method with the main objective of creating the connection object, making the search call of the
# tweets and returning a list of the tweets.
def search_tweet_list(query, max_results):
    log.info('Looking for tweets')
    # Object of connection
    client, api = get_client()
    # Searching for tweets
    tweets = search_tweets_user(client, query, max_results)
    log.info(f'Found tweets: {tweets}')
    # Creating list of tweets
    objs = []
    if len(tweets) > 0:
        for tweet in tweets:
            twt = get_tweet(client, tweet['id'])
            objs.append({
                'text': tweet['text'],
                'username': twt.includes['users'][0].username,
                'id': tweet['id'],
                'url': 'https://twitter.com/{}/status/{}'.format(twt.includes['users'][0].username, tweet['id'])
            })
    return objs, client, api


# Method responsible for posting the tweets
def tweet_to_publish(text, query):
    # Before posting we check if we already have tweets for that query
    # today
    tweets, client, api = search_tweet_list(query, 10)
    if tweets:
        # if we already have tweeted about it today we create a sequential post
        # For this to happen we get the id of the tweet we want to follow
        return client.create_tweet(text=text, in_reply_to_tweet_id=tweets[0]['id'])
    else:
        # if there are no posts on the day we create a new post
        return client.create_tweet(text=text)


def tweet_to_publish_with_image(text, query, imgs):
    log.info('Starting post')
    try:
        client, api = get_client()
        api.update_status(status=text)
        log.info('Header posted')
        log.info('Waiting broadcasting')
        sleep(25)
        tweets, client, api = search_tweet_list(query, 10)
        if tweets:
            # if we already have tweeted about it today we create a sequential post
            # For this to happen we get the id of the tweet we want to follow
            for key, value in imgs.items():
                log.info(f'Tweeting image: {value}')
                media = api.media_upload(value)
                api.update_status(status=key, media_ids=[media.media_id], in_reply_to_status_id=tweets[0]['id'])
                log.info('Waiting broadcasting.')
                sleep(25)
                tweets, client, api = search_tweet_list(f'{key} -is:retweet', 10)
    except BaseException as err:
        log.error(f'There was an error trying to post the images. Error: {err}')