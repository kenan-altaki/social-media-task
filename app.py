import asyncio
import aiohttp
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])        # Only allow get requests
async def social_network_activity():    # make async coroutine

    activity = {}

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch(activity, session, 'facebook',
                  'https://takehome.io/facebook'),
            fetch(activity, session, 'twitter', 'https://takehome.io/twitter'),
            fetch(activity, session, 'instagram',
                  'https://takehome.io/instagram'),
        ]
        await asyncio.gather(*tasks)

    json_response = jsonify(activity)
    return json_response


async def fetch(activity, session, name, url):
    async with session.get(url) as response:
        try:
            results = await response.json()
            activity[name] = len(results)

        except Exception as e:
            print('Exception!', e)
