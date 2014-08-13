import time
import praw
import sys
import os

""" 
==========================================================================

Enable or diable debug output.  I put this at the top because I'm
too lazy to scroll down if I want debug verbosity.

==========================================================================
"""

DEBUG = 0


"""
=========================================================================
SnooBot
by bgm

VERSION: 0.00000000000000000000000000000000000000000001
Seriously.  This thing is like super-alpha right now.

The only real dependencies this thing requires is time,
praw, and sys.

The idea of this bot is to scour /r/askreddit for posts
marked with the [Stories] tag (or [stories] or [story], etc)
and when it finds such a post, it counts the amount of 
replies to it.

If there are sufficient replies, it builds links to each
story and then aggregates them all into a single post.

Hopefully, it will make finding interesting stories easier
as the post ages.

Future functionality will include:
	- better exception handling.
	- a better look on mobile devices.
	- functionality for lower-level posts.

Shoot me an email at ninjanerdbgm@gmail.com if you have
any questions.
==========================================================================
"""

print("SnooBot v 0.0000000000000000001.")

"""
==========================================================================

Let's set our user agent that we'll use for reddit below.
It can be whatever, but I hear it's best practice to not
hide the fact that it's a bot.

==========================================================================
"""

r = praw.Reddit('AskReddit [Stories] Aggregator Bot, v 0.00000000001'
                'Seriously.  This thing is in, like, super alpha.'
                'by /u/ninjanerdbgm')

"""
==========================================================================

Okay, now we log in.

==========================================================================
"""

print("Attempting to connect to reddit...")


loggedin=0
while loggedin==0:
	try:
		r.login('StoryAggregatorBot', 'ishouldprobablychangethis1')
		loggedin=1
	except:
		print("Unable to connect.  Reddit might be down.  Trying again in a few minutes...")
		time.sleep(300)
print("Success!") # Whoo hoo!

"""
==========================================================================

I initialize a few arrays here that I'll use later.

already_done: this keeps track of which submissions we've checked this round.
skip_posts: have we been downvoted to oblivion?  Let's mark it here.

==========================================================================
"""

already_done = []
skip_posts = []

"""
==========================================================================

Here's the main loop that looks through /r/AskReddit.

But first, let's make a list of some of the common ways to write the tag.
We'll use this shortly.

==========================================================================
"""

storytags = ['[stories]', '[story]', '[ stories]', '[stories ]', '[ stories ]', 'stories only']

while True: # Begin the bot loop.  Run until ctrl+c, or until it hits an exception.

	print("Searching /r/askreddit for [Story] posts...")
        subreddit = r.get_subreddit('askreddit')

        for submission in subreddit.get_hot(limit=500): # This limit could be changed if you want.  I tried with 250 and it didn't pick up much.  
							# I tried with 1000 and it took FOREVER to run.
                """
		==========================================================================

                Find the [Stories] tag.  

		To do this, we convert each title into lowercase to make matching
		easier.  At this point, it might be prudent to put a try: operator since
		this seems like something that could error out (if reddit is down
		or whatever).

		==========================================================================
                """

                titletolower = submission.title.lower()
                isstory = any(string in titletolower for string in storytags)

                if submission.id not in already_done and isstory:
                        print("Story found! \"{}\"\nHere's a link: {}".format(submission.title,submission.short_link))

			if submission.id in skip_posts:
				print("Oh, man.  Actually, they already downvoted the bot out of here.  Let's just skip this one and keep our heads down.")
                        else:	
				edit_comments = [] # I initialize the array to keep comments to edit now.  It could just be a variable, but an array is safer.
	                        submission.replace_more_comments(limit=None, threshold=0) # This makes it grab EVERY top-level comment instead of the first 50 or so.

	                        """ Is it a popular post?  If not, skip it and don't add it to the miss list.  We'll get to it later. """

	                        numcoms = 0
				madepost = 0
	
				"""
				==========================================================================

				Why use the loop below to count comments instead of just grabbing the comments number
				from the API dictionary?  Because it counts all comments of all levels.  
				Our bot needs to match top-level comments only.  This lets us do that.

				==========================================================================
				"""

	                        for comment in submission.comments:
	                                numcoms+=1

	                        print("        | Total number of comments on this story: {0}".format(numcoms))


	                        if numcoms > 15:
	                                print("        | Building submission reply.")
					
					"""
					==========================================================================

					Let's start building a comment using reddit table format.

					==========================================================================
					"""

	                                makeaggregate = "Hello!  I am an aggregator bot designed to make it easier to find the stories posted in this topic.  Below is a list of stories:\n\nStory Blurb | Author\n--- | ---"

					print("        | ======================================================================\
						\n        | Hello! I am an aggregator bot designed to make it easier to find the stories posted in this topic.  Below is a list of stories:\n\n        | Story Blurb | Author\
	                                        \n        | --- | ---".format(makeaggregate))

	                                already_covered = set() # This is similar to already_done above, but for comments instead of submissions.

	                                """ Now let's look for stories """

	                                for comment in submission.comments:
						if DEBUG == 1:
							print("        | DEBUG: Comment length: {0}".format(len(comment.body)))

						if len(comment.body) > 250 and comment.id not in already_covered:
	                                                author = comment.author
							if author.name <> "xAutoModeratorx": # We don't want to aggregate AutoMod posts, do we?  NO.  THE ANSWER IS NO.
		                                                """ 
								==========================================================================

								Let's check if the comment we found was the bot's own comment.
								If it was, then we'll make a note to edit it later and skip it as
		                                                part of the aggregated posts.

								==========================================================================
		                                                """
		                                                if author.name == "StoryAggregatorBot": # We also don't want to aggregate our own posts, if you were wondering.
		                                                        edit_comments.append(comment)   # BUT, we do want to mark it as a post we should edit later.
									madepost = 1			# Just in case there were updates.
								else:
			                                                a=0
			                                                comlink=""

			                                                while a < 80:
										try: 
											if chr(ord(comment.body[a])) == chr(13) or chr(ord(comment.body[a])) == chr(10):
												""" Let's replace line feeds with spaces to keep the format """
												comlink+=" "
											else:
					                                                        comlink+=(chr(ord(comment.body[a]))) # There might be an easier way to do this.
												# I'm not sure if comment.body[a] would return the character itself or something
												# else.  So I throw it in ord to translate it to ascii, then into chr to turn it
												# back into an actual character.  It's just as a failsafe.
					                                                a+=1
										except:
											"""
											==========================================================================
	
											I added this exception because I was running into some weird shit
											while copying and pasting long articles during tests.
											This *should* fix most issues.  Let me know if you find something.

											==========================================================================
											"""
											print("        | (((Encountered a strange encoding.  Let's replace it with null.)))")
											comlink+=""
											a+=1

			                                                url = submission.permalink	# Grab the submission url
			                                                url += comment.id 		# Now tack on the link to the individual comment
			                                                comlink += "..."		# Add elipses to the story blurb
			                                                makeaggregate += "\n[{0}]({1}) | /u/{2}".format(comlink, url, author.name) # Generate a link to each story in reddit table format.
									print("        | [{0}]({1}), by {2}".format(comlink, url, author.name))
									time.sleep(0.05) # Threw this in here to better clean up the terminal output.  Makes it look shiny.
		        	                                        already_covered.add(comment.id) # Toss this comment in the list of ones we've covered.

					"""
					==========================================================================

					OKAY COMMENTS SCRAPED GAISE LETS DO A FOOTER HURR HURR

					==========================================================================
					"""

	                                makeaggregate += "\n\nPlease downvote this bot if you find it annoying and it will delete the post automatically.\
							\n\n[^Send ^message ^to ^creator](http://www.reddit.com/message/compose/?to=ninjanerdbgm) ^| [^What ^is ^a ^bot?](http://www.reddit.com/r/botwatch/wiki/faq) ^|\
							[^Did ^this ^bot ^mess ^up?  ^Let ^me ^know!](http://www.reddit.com/message/compose/?to=ninjanerdbgm) ^| [^Source ^Code](https://github.com/ninjanerdbgm/SAB)"

					"""
					==========================================================================
	
					DONE FOOTER STUFF

					==========================================================================
					"""

					print("        | Please downvote this bot if you find it annoying and it will delete the post automatically.")
					print("        | ================================================================\n        | Attempting to send post query...")

	                                """ Is this a new post or one we should edit? """

	                                if madepost == 0: # New post.
			              	    try:
	                                              	submission.add_comment(makeaggregate)
							already_done.append(submission.id)
							print("        | Successfully posted a message!")
				            except RateLimitExceeded:
							print("        | Ahhhh I'm posting too much and making reddit angry.  I'm just going to back off for a bit and try again later.")
							pass # Put something here later, maybe.

	                                else:		  # One we should edit.
						for comments in edit_comments:
							comments.edit(makeaggregate)
							edit_comments.remove(comments)
							print("        | Successfully edited a message!")
	
	                        else: # It was a while ago, but this is called when there are less than 15 comments on the story post.

	                                print("        | At {0} comments, this post isn't popular enough for a submission, yet.".format(numcoms))
	
	"""
	==========================================================================

	Alright, comment scraping is done.  Let's do some bot cleanup.
	First, let's check if any posts the bot made have been downvoted
	into oblivion.

	==========================================================================
	"""

	print("----------------------------------------------------------------------")
	print("Couldn't find anymore reddit posts for the time being.  Let's move on!")

        """ Look for unpopular posts """

        print("Looking for unpopular bot posts...")
        user = r.get_redditor("StoryAggregatorBot") # We wanna find our own posts.
        for i in user.get_comments(limit=300):      # The limit here can be changed, but 300 posts is sufficient history for what we're trying to do.
		if DEBUG == 1:
			print("        | DEBUG: Comment score: {0}".format(i.score))

		print("        | Comment to post: \"{0}\" with an id of {1} currently has a score of {2}\n         ---> Post can be found here: {3}".format(i.submission.title,i.id,i.score,i.permalink))

      		if i.score <= 0: # Did some asshole downvote my bot to hell?
                        print("         ---> Ouch, it has a pretty low score.  Let's delete it.")
			skip_posts.append(i.submission.id)
       		        i.delete() # Appease the assholes.

        """ ======================== """

	print("Done!")
	print("----------------------------------------------------------------------")

	time.sleep(1)
	i=600
	secs=0

	"""
	==========================================================================

	Alright, all done.  Now we'll sleep for 10 minutes and try again.
	This can be modified, just change the variable i, above, to however
	many seconds you want to wait.

	The following bit of code counts down one second at a time, and outputs
	the remaining time in mm:ss format.

	==========================================================================
	"""

	while i > 0:
#		os.system('clear') # This is old.  This cleared the screen, but I've removed it in favor of stdout.write and .flush to make it look better.
		sys.stdout.write("This round of scouring is over!  {0:0>2}:{1:0>2} until the next round!\r".format((i/60),(i%60)))
		sys.stdout.flush()
		time.sleep(1)
		i-=1

        print("-------------------------------------------")	

"""
==========================================================================

END OF BOT

...

for now

==========================================================================
"""

