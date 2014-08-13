import time
import praw
import sys, time
import os

""" Enable or diable debug output """
DEBUG = 0
""" ============================= """

"""
SnooBot
by bgm

VERSION: 0.00000000000000000000000000000000000000000001

Seriously.  This thing is like super-alpha right now.



Idle in chat and follow some basic commands to get stuff from reddit.
"""

print("SnooBot v 0.0000000000000000001.")

r = praw.Reddit('AskReddit [Stories] Aggregator Bot, v 0.00000000001'
                'Seriously.  This thing is in, like, super alpha.'
                'by /u/ninjanerdbgm')

print("Attempting to connect to reddit...")
loggedin=0
while loggedin==0:
	try:
		r.login('StoryAggregatorBot', 'ishouldprobablychangethis1')
		loggedin=1
	except:
		print("Unable to connect.  Reddit might be down.  Trying again in a few minutes...")
		time.sleep(300)
print("Done!")

already_done = []
skip_posts = []

"""
Here's the main loop that looks through /r/AskReddit
"""

"""
First, let's make a list of some of the common ways to write the tag
"""

storytags = ['[stories]', '[story]', '[ stories]', '[stories ]', '[ stories ]', 'stories only']

while True:
	print("Searching /r/askreddit for [Story] posts...")
        subreddit = r.get_subreddit('askreddit')
        for submission in subreddit.get_hot(limit=500):
#	    try:
                """
                Find the [Stories] tag
                """
                titletolower = submission.title.lower()
                isstory = any(string in titletolower for string in storytags)

                if submission.id not in already_done and isstory:
                        msg = 'Found a story!  Here\'s a link: {0}'.format(submission.short_link)
                        print(msg)
			if submission.id in skip_posts:
				print("Oh, man.  Actually, they already downvoted the bot out of here.  Let's just skip this one and keep our heads down.")
                        else:
				edit_comments = []
	                        submission.replace_more_comments(limit=None, threshold=0)
	                        """ Is it a popular post?  If not, skip it and don't add it to the miss list.  We'll get to it later. """
	                        numcoms = 0
				madepost = 0
	                        for comment in submission.comments:
	                                numcoms+=1
	                        print("        | Total number of comments on this story: {0}".format(numcoms))
	                        if numcoms > 15:
	                                print("        | Building submission reply.")
	                                makeaggregate = "Hello!  I am an aggregator bot designed to make it easier to find the stories posted in this topic.  Below is a list of stories:\n\nStory Blurb | Author\n--- | ---"
					print("        | ======================================================================\
						\n        | Hello! I am an aggregator bot designed to make it easier to find the stories posted in this topic.  Below is a list of stories:\n\n        | Story Blurb | Author\
	                                        \n        | --- | ---".format(makeaggregate))
	                                already_covered = set()
	                                """ Now let's look for stories """
	                                for comment in submission.comments:
						if DEBUG == 1:
							print("        | DEBUG: Comment length: {0}".format(len(comment.body)))
						if len(comment.body) > 250 and comment.id not in already_covered:
	                                                author = comment.author
							if author.name <> "xAutoModeratorx":
		                                                """ Let's check if the comment we found was the bot's own comment.
		                                                    If it was, then we'll make a note to edit it later and skip it as
		                                                    part of the aggregated posts.
		                                                """
		                                                if author.name == "StoryAggregatorBot":
		                                                        edit_comments.append(comment)
									madepost = 1
								else:
			                                                a=0
			                                                comlink=""
			                                                while a < 80:
										try: 
											if chr(ord(comment.body[a])) == chr(13) or chr(ord(comment.body[a])) == chr(10):
												""" Let's replace line feeds with spaces to keep the format """
												comlink+=" "
											else:
					                                                        comlink+=(chr(ord(comment.body[a])))
					                                                a+=1
										except:
											print("        | (((Encountered a strange encoding.  Let's replace it with null.)))")
											comlink+=""
											a+=1
			                                                url = submission.permalink
			                                                url += comment.id
			                                                comlink += "..."
			                                                makeaggregate += "\n[{0}]({1}) | /u/{2}".format(comlink, url, author.name)
									print("        | [{0}]({1}), by {2}".format(comlink, url, author.name))
									time.sleep(0.05)
		        	                                        already_covered.add(comment.id)
	                                makeaggregate += "\n\nPlease downvote this bot if you find it annoying and it will delete the post automatically.\
							\n\n[^Send ^message ^to ^creator](http://www.reddit.com/message/compose/?to=ninjanerdbgm) ^| [^What ^is ^a ^bot?](http://www.reddit.com/r/botwatch/wiki/faq) ^|\
							[^Did ^this ^bot ^mess ^up?  ^Let ^me ^know!](http://www.reddit.com/message/compose/?to=ninjanerdbgm) ^| [^Source ^Code](https://github.com/ninjanerdbgm/SAB)"
					print("        | Please downvote this bot if you find it annoying and it will delete the post automatically.")
					print("        | ================================================================\n        | Attempting to send post query...")
	                                """ Is this a new post or one we should edit? """
	                                if madepost == 0:
			              	    try:
	                                              	submission.add_comment(makeaggregate)
							already_done.append(submission.id)
							print("        | Successfully posted a message!")
				            except RateLimitExceeded:
							print("        | Ahhhh I'm posting too much and making reddit angry.  I'm just going to back off for a bit and try again later.")
							pass # Put something here later, maybe.
	                                else:
						for comments in edit_comments:
							comments.edit(makeaggregate)
							edit_comments.remove(comments)
							print("        | Successfully edited a message!")
	                        else:
	                                print("        | At {0} comments, this post isn't popular enough for a submission, yet.".format(numcoms))
#            except:
#			print("Evidently, something went wrong while trying to search for posts.  Reddit may be down for maintainence.  Let's just take a nap for a while and try again later.")
	print("----------------------------------------------------------------------")
	print("Couldn't find anymore reddit posts for the time being.  Let's move on!")
        """ Look for unpopular posts """
        print("Looking for unpopular bot posts...")
        user = r.get_redditor("StoryAggregatorBot")
        for i in user.get_comments(limit=300):
				if DEBUG == 1:
					print("        | DEBUG: Comment score: {0}".format(i.score))
				print("        | Comment to post: \"{0}\" with an id of {1} currently has a score of {2}\n         ---> Post can be found here: {3}".format(i.submission.title,i.id,i.score,i.permalink))
                		if i.score <= 0:
		                        print("         ---> Ouch, it has a pretty low score.  Let's delete it.")
					skip_posts.append(i.submission.id)
                		        i.delete()
        """ ======================== """
	print("Done!")
	print("----------------------------------------------------------------------")
	time.sleep(1)
	i=600
	secs=0
	while i > 0:
#		os.system('clear')
		sys.stdout.write("This round of scouring is over!  {0:0>2}:{1:0>2} until the next round!\r".format((i/60),(i%60)))
		sys.stdout.flush()
		time.sleep(1)
		i-=1
        print("-------------------------------------------")	

