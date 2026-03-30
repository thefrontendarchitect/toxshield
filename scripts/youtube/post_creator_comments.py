"""
Post unique creator comments to all ToxShield YouTube videos.
Run once — posts a funny, relatable first comment from the channel owner on each video.
"""
import os
import time
from dotenv import load_dotenv

load_dotenv('/Users/biswa/toxshield/.env.local')
load_dotenv('/Users/biswa/toxshield/.env')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

client_id = os.getenv('YOUTUBE_CLIENT_ID')
client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

creds = Credentials(
    token=None,
    refresh_token=refresh_token,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=client_id,
    client_secret=client_secret,
    scopes=['https://www.googleapis.com/auth/youtube']
)

youtube = build('youtube', 'v3', credentials=creds)

# Each comment is unique to its video topic — funny, relatable, ends with a hook
comments = [
    {
        'video_id': 'U837Irc84dE',
        'title': 'My Ex Said He Was an Empath | ToxShield Comedy #Shorts',
        'comment': (
            "I made this video and then immediately remembered every time he cried at a commercial "
            "but somehow never noticed when I was crying \U0001f480 "
            "Drop a \U0001f6a9 if your ex's \"empathy\" only ever activated when they needed something from you"
        )
    },
    {
        'video_id': 'hNd4zRljzhY',
        'title': 'My ex was a future faker. She planned our wedding and breakup on the same week #Shorts',
        'comment': (
            "Future fakers are genuinely built different \u2014 they can cry at the wedding venue "
            "they already plan to ghost you from \U0001f62d "
            "What's the most elaborate future they sold you that never came true?"
        )
    },
    {
        'video_id': 'EknpkMOvp8U',
        'title': 'The Cycle That Keeps You Trapped (Idealize, Devalue, Discard)',
        'comment': (
            "The wildest part? Once you learn the cycle you can PREDICT when the devalue phase is coming "
            "and you still stay \U0001f643 "
            "Like knowing the jump scare is coming and still screaming. "
            "Drop a \U0001f504 if you've been through this loop more than once"
        )
    },
    {
        'video_id': 'R5hBblLbL4A',
        'title': "7 Signs You're Trauma Bonded (Not In Love)",
        'comment': (
            "Trauma bonding is terrifying because you're not in love with them \u2014 "
            "you're in love with who they were on a random Tuesday in month two. "
            "That person was never real. Pour one out \U0001f942 Which sign hit the hardest?"
        )
    },
    {
        'video_id': '3ovQemXDqGY',
        'title': "5 Signs You're Being Gaslighted (They Sound Normal)",
        'comment': (
            "I made this video and my brain immediately went \"wait, I've said "
            "'maybe you're right' to someone who was definitely not right\" \U0001f480 "
            "Drop a \U0001f6a9 if #3 made your stomach drop"
        )
    },
    {
        'video_id': 'qEjMlNUVr5Q',
        'title': 'I Analyzed a Love Bomber \u2014 The Score Will Shock You',
        'comment': (
            "8.7/10 and he still had her blocked by the time this uploaded. "
            "Love bombing speedrun any% \U0001f3c3 "
            "What's the fastest someone went from \"you're my soulmate\" to a complete stranger?"
        )
    },
    {
        'video_id': 'IuNNYJwXG9I',
        'title': 'I Analyzed a DARVO Manipulator \u2014 Score: 9.1 (The Truth)',
        'comment': (
            "9.1/10 and somehow YOU were the one apologizing by the end of every single fight. "
            "The algorithm just confirmed what your gut already knew \U0001f9e0 "
            "Drop a \U0001f624 if you ever apologized for bringing up something completely valid"
        )
    },
    {
        'video_id': 'iXY7T8Q3Lt4',
        'title': '"After Everything I\'ve Done for You" \u2014 DARVO',
        'comment': (
            "\"After everything I've done for you\" is the DARVO starter pack \u2014 "
            "deploys the second accountability enters the chat \U0001fae1 "
            "What triggered yours? Mine was literally just asking why they were late"
        )
    },
    {
        'video_id': 'Zcu4_Tl45iA',
        'title': '"Why Are You So Boring Now?" \u2014 The Grey Rock Method',
        'comment': (
            "Grey rock is just playing dead until the bear leaves \U0001f43b "
            "And when they call you boring, you KNOW it's working. "
            "Drop a \U0001fab8 if grey rock changed your life"
        )
    },
    {
        'video_id': 'RXEEfCa5D-Q',
        'title': '"He\'s Just Stressed" \u2014 500 Scores Say Otherwise',
        'comment': (
            "500 relationships. 67% scored 6+. "
            "\"He's just stressed\" is genuinely one of the most load-bearing sentences in the English language \U0001f605 "
            "How many years did you carry that excuse? toxshield.in has the receipts"
        )
    },
    {
        'video_id': 'UJOQf_7rAXY',
        'title': '"You\'re the Problem Here" \u2014 That\'s DARVO',
        'comment': (
            "You raised a totally reasonable concern and somehow ended up in the apology seat. "
            "Every. Single. Time. \U0001f643 "
            "The pipeline from \"I need to talk about something\" to \"I'm sorry for bringing it up\" "
            "is a 3-minute speedrun with some people. Sound familiar?"
        )
    },
    {
        'video_id': '1Wk4XUem2Ak',
        'title': '"That Never Happened" \u2014 The #1 Gaslighting Phrase',
        'comment': (
            "\"That never happened\" is wild because you KNOW it happened. You were there. "
            "And somehow they say it with such confidence you start Googling early memory loss \U0001f480 "
            "What's the most specific thing someone insisted never happened to you?"
        )
    },
    {
        'video_id': '4-ocLAQg5s8',
        'title': '"You\'re Too Sensitive" \u2014 That\'s Gaslighting',
        'comment': (
            "\"You're too sensitive\" said by the person who caused the thing you're being sensitive about \U0001f643 "
            "The audacity is genuinely a skill set. "
            "Drop a \u270b if you spent years believing you were the problem"
        )
    }
]

results = []
errors = []

print(f"Posting {len(comments)} creator comments...\n")

for item in comments:
    try:
        response = youtube.commentThreads().insert(
            part='snippet',
            body={
                'snippet': {
                    'videoId': item['video_id'],
                    'topLevelComment': {
                        'snippet': {
                            'textOriginal': item['comment']
                        }
                    }
                }
            }
        ).execute()
        comment_id = response['id']
        results.append({
            'video_id': item['video_id'],
            'title': item['title'],
            'comment': item['comment'],
            'comment_id': comment_id,
            'status': 'SUCCESS'
        })
        print(f"OK  [{item['video_id']}] {item['title'][:65]}")
        time.sleep(1.5)  # Be gentle with the quota
    except Exception as e:
        errors.append({
            'video_id': item['video_id'],
            'title': item['title'],
            'error': str(e)
        })
        print(f"FAIL [{item['video_id']}] {item['title'][:65]}")
        print(f"     Error: {str(e)[:120]}")
        time.sleep(1.5)

print(f"\n{'='*60}")
print(f"SUMMARY: Posted {len(results)}/{len(comments)} comments")
if errors:
    print(f"Failed:  {len(errors)}")
    for e in errors:
        print(f"  [{e['video_id']}] {e['error'][:120]}")

print(f"\n{'='*60}")
print("ALL POSTED COMMENTS:")
print(f"{'='*60}")
for r in results:
    print(f"\nVideo: {r['title']}")
    print(f"  ID:      {r['video_id']}")
    print(f"  Comment ID: {r['comment_id']}")
    print(f"  Comment: {r['comment']}")
