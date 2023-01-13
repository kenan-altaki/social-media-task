import asyncio
import aiohttp
from flask import Flask, jsonify
from flask_cors import CORS


# =============================================================================
# # Assumptions made
# =============================================================================
#  - Speed > Robustness
#      - use multi-threading to fetch data.
#      - use `aiohttp` rather than `requests`
#      - since the latter is not thread-safe.
#      - use `asyncio` rather than `threading`.
#  - Robustness > Correctness
#      - if incomplete/wrong data is recieved,
#      - flag it as wrong and return a response
#      - do not abort request,
#      - and do not attempt a retry due to speed requirements
# =============================================================================

# List of API endpoints names and their urls to be queried.
# This allows us to scale up and down without much effort.
API_LIST = [
    {'name': 'facebook', 'url': 'https://takehome.io/facebook'},
    {'name': 'twitter', 'url': 'https://takehome.io/twitter'},
    {'name': 'instagram', 'url': 'https://takehome.io/instagram'},
]

# Some options
FAIL_ON_UNHANDLED_EXCEPTION = True

app = Flask(__name__)

# CORS!
# Needed when client app is not on the same host. Learned this the hard way!!!
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
                # This is the expected Exception, when the GET request does not
                # receive a properly formatted JSON.
                print('ContentTypeError!', e)
                # Set the value of the activity to `null` and continue.
                # Based on assumption 2 above.
                # `null` is the correcter way to pass it in JSON.
                activity[name] = None

            except Exception as e:
                # It is generally a bad idea to catch all exceptions.
                # Since it eliminates the ability to respond to diferent
                # errors adequately.
                #
                # A better idea is to discuss this with the client and agree
                # on a suitable way to pass/handle them.
                print('Exception!', e)

                # Set the value of the activity to `-1`, to indicate a different
                # type of error to the expected one.This value will be sent to
                # client if FAIL_ON_UNHANDLED_EXCEPTION = False
                activity[name] = -1

                # For now, set an option that can be changed if you want to not
                # carry on on an unhandled exception.
                if FAIL_ON_UNHANDLED_EXCEPTION:
                    return '', 500

    async with aiohttp.ClientSession() as session:
        # Create the session object in context and generate the tasks.
        tasks = [
            fetch(session, api['name'], api['url'])
            for api in API_LIST
        ]

        await asyncio.gather(*tasks)

    return jsonify(activity), 200
