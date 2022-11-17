import random
import string


STRING_ID_SIZE=16

# function to generate the 16 digit unique id for track the request
def generate_unique_id():
    unique_id_16 = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(STRING_ID_SIZE)])
    return unique_id_16


