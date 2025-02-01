
def slug(x, id):
    return f'{x}/{id}.json' # Eg. SLUG('item/8863') 

def get_arg(msg):
    msg = " ".join(msg.strip().split(' ')[1:])
    return msg