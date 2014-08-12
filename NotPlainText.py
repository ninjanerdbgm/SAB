"""
This is an old dependency.  I was messing around with encoding plaintext during authentication.
This can be ignored.
"""

def encode(string):
	s = string
	""" Get string length.  Also, using trip quotes for one-line comments is dumb, but it's easier to read in bash. """
	slen = len(s)
	output = ""
	i = 0
	while i < slen:
		""" Let's check for spaces """
		if s[i] == chr(32):
			output += chr(92)
		else:
			""" Encode the string using some arbitrary(?) value """
			output+=chr((ord(s[i]) + (98 ** 103 * 109)) % 66)
		i+=1

	return output

def decode(string):
	s = string
	""" Comments here would be the same as above, but in reverse, so yeah. """
	slen = len(s)
	output = ""
	i = 0
	while i < slen:
		""" Let's check for spaces, quotes, pound signs.. anything that doesn't play well in python code """
		if s[i] == chr(92):
			output += chr(32);
		""" Or just spaces.  Whatever. """
		else:
			output+=chr((ord(s[i]) - (98 ** 103 * 109)) % 66)
		i+=1

	return output
