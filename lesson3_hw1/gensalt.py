import random
import string

# implement the function make_salt() that returns a string of 5 random
# letters use python's random module.
# Note: The string package might be useful here.
ALLOWED_CHARS = string.digits + string.letters
random.seed()

def make_salt(salt_len=5):
    ###Your code here
    salt = ''
    for i in xrange(salt_len):
        salt += random.choice(ALLOWED_CHARS)
    return salt
