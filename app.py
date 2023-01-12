import asyncio
import aiohttp
from flask import Flask, jsonify

# List of API endpoints names and their urls to be queried.
API_LIST = [
    {'name': 'facebook', 'url': 'https://takehome.io/facebook'},
    {'name': 'twitter', 'url': 'https://takehome.io/twitter'},
    {'name': 'instagram', 'url': 'https://takehome.io/instagram'},
]


app = Flask(__name__)


@app.route('/', methods=['GET'])        # Only allow get requests
async def social_network_activity():    # make async coroutine

    activity = {}

    async def fetch(session, name, url):
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
        tasks = [
            fetch(session, api['name'], api['url'])
            for api in API_LIST
        ]
        await asyncio.gather(*tasks)

    json_response = jsonify(activity)
    return json_response
