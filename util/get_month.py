#!/usr/bin/python3
from dateutil.parser import parse
import datetime
import pymongo

if __name__ == '__main__':
    client = pymongo.MongoClient("localhost", 27017)
    print("Successfully connected to mongo")
    db = client.facebook # use the facebook database (automatically created if it doesn't exist)
    posts = db.posts
    comments = db.comments

    print("Fetching all posts...", datetime.datetime.now())
    all_posts = list(posts.find({"year": {"$exists": False}}))
    print("Finished fetching all posts...", datetime.datetime.now())
    print("Updating all posts...", datetime.datetime.now())
    for p in all_posts:
        p['month'] = p['created_time'].month
        p['year'] = p['created_time'].year
        posts.update({'_id': p['_id']}, p)
    print("Finished updating all posts...", datetime.datetime.now())

    print("Fetching all comments...", datetime.datetime.now())
    all_comments = list(comments.find({"year": {"$exists": False}}))
    print("Finished fetching all comments...", datetime.datetime.now())
    print("Updating all comments...", datetime.datetime.now())
    for c in all_comments:
        c['month'] = c['created_time'].month
        c['year'] = c['created_time'].year
        comments.update({'_id': c['_id']}, c)
    print("Finished updating all comments...", datetime.datetime.now())
