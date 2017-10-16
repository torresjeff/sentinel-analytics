#!/usr/bin/python3
from model import Facebook

if __name__ == '__main__':
    fb = Facebook()
    
    all_posts = fb.query('posts', {})
    for p in all_posts:
        reactions = fb.get_reactions_for_post(p['_id'])
        if reactions is not None:
            p['angry'] = reactions['angry']
            p['like'] = reactions['like']
            p['haha'] = reactions['haha']
            p['sad'] = reactions['sad']
            p['love'] = reactions['love']
            p['wow'] = reactions['wow']
    
    fb.update_all('posts', all_posts)