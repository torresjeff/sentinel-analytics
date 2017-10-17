#!/usr/bin/python3
import sys, os
lib_dir = os.environ.get('HOME')
lib_dir += '/workspace/analytics/util'
sys.path.append(lib_dir)
from model import Facebook

class Counter:
    def get_activity_count(self, post_list):
        angry = 0
        like = 0
        haha = 0
        sad = 0
        love = 0
        wow = 0
        shares = 0

        for p in post_list:
            if 'angry' in p: angry += p['angry']
            if 'like' in p: like += p['like']
            if 'haha' in p: haha += p['haha']
            if 'sad' in p: sad += p['sad']
            if 'love' in p: love += p['love']
            if 'wow' in p: wow += p['wow']
            if 'shares' in p: shares += p['shares']
        
        result = {
            "angry": angry,
            "like": like,
            "haha": haha,
            "sad": sad,
            "love": love,
            "wow": wow,
            "shares": shares
        }

        return result


if __name__ == '__main__':
    fb = Facebook()
    