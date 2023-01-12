import asyncio
import aiohttp
from flask import Flask, jsonify
from flask_cors import CORS


# List of API endpoints names and their urls to be queried.
API_LIST = [
    {'name': 'facebook', 'url': 'https://takehome.io/facebook'},
    {'name': 'twitter', 'url': 'https://takehome.io/twitter'},
    {'name': 'instagram', 'url': 'https://takehome.io/instagram'},
]

'''
# Assumptions made

 - Speed > Robustness
     - use multi-threading to fetch data.
     - use `aiohttp` rather than `requests`
     - since the latter is not thread-safe.
     - use `asyncio` rather than `threading`.
 - Robustness > Correctness
     - if incomplete/wrong data is recieved, 
     - flag it as wrong and return a response
     - do not abort request, 
     - and do not attempt a retry due to speed requirements
'''

app = Flask(__name__)

# CORS!
# needed when client app is not on the same host
# learned this the hard way!!!
cors = CORS(app)

@app.route('/', methods=['GET'])        # Only allow get requests
async def social_network_activity():    # make async coroutine
    '''Social network activity endpoint.

    Returns a JSON object with the level of activity of each social network.
    Returns -1 if unable to get network activity
    '''

    # store the results in this dict
    activity = {}

    async def fetch(session, name, url):
        '''The async function that does the work.
        
        Function that fetches the data from APIs defined up top.
        Attempts to parse the body of the response into JSON, and if successful 
        returns the activity level. Otherwise `null` if cannot parse or `-1` 
        if undefined error.
        '''
        async with session.get(url) as response:
            try:
                results = await response.json()
                activity[name] = len(results)

            except aiohttp.ContentTypeError as e:
                # this is the expected Exception, when the GET request does 
                # not receive a properly formatted JSON
                print('ContentTypeError!', e)
                activity[name] = None
                # `null` is the correcter way to pass it in JSON

            except Exception as e:
                # for all other Exceptions
                print('Exception!', e)
                activity[name] = -1

    async with aiohttp.ClientSession() as session:
        # create the session object in context and generate the 
        # tasks for `asyncio`.`gather()`
        tasks = [
            fetch(session, api['name'], api['url'])
            for api in API_LIST
        ]
        await asyncio.gather(*tasks)

    return jsonify(activity), 200
