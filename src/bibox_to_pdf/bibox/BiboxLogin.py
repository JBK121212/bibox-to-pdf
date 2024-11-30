import asyncio
import base64
import hashlib
import secrets
import sys

import requests
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from rich import print as rprint

from bibox_to_pdf.values.Constants import Constants

login_endpoint_queue = asyncio.Queue()

app = FastAPI()
config = uvicorn.Config(app, host='0.0.0.0', port=4200, log_level="warning")
server = uvicorn.Server(config)

@app.get('/login', response_class=HTMLResponse)
async def login(req: Request, background_tasks: BackgroundTasks):
    code = req.query_params.get('code')
    if code is None:
        return '<h1>Error: Code is missing from request params</h1>'

    background_tasks.add_task(login_endpoint_queue.put, code)

    return '<h1>You can close this window now</h1>'


async def start_webserver():
    try:
        await server.serve()
    except Exception as e:
        rprint(f'Error starting webserver: {e}')
        sys.exit(1)

def create_login_link():
    login_url = Constants.biboxOauthLoginUrl
    client_id = Constants.biboxOauthClientId
    redirect_uri = 'http://localhost:4200/login'
    code_verifier = secrets.token_urlsafe(96)[:96]

    code_verifier_hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_verifier_encoded = base64.urlsafe_b64encode(code_verifier_hashed)
    code_challenge = code_verifier_encoded.decode('ascii')[:-1]

    login_url = login_url + f'?client_id={client_id}&response_type=code&scope=openid&redirect_uri={redirect_uri}&code_challenge_method=S256&code_challenge={code_challenge}'

    return {
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
        'login_url': login_url,
    }

def get_access_token(code: str, code_verifier: str, redirect_uri: str) -> str:
    token_endpoint = Constants.biboxOauthTokenUrl

    token_result = requests.post(token_endpoint, data={
        'redirect_uri': redirect_uri,
        'code': code,
        'code_verifier': code_verifier,
    })

    if token_result.status_code != 201 | 200:
        raise Exception(f'Error getting access token: {token_result.text}')

    return token_result.json().get('access_token')


async def login_to_bibox() -> str:
    # Create a task in a separate thread with a webserver to handle the login callback
    webserver_task = asyncio.create_task(start_webserver())

    while True:
        login_result = create_login_link()
        rprint('To log in to bibox open the following link in your browser: ')
        print(login_result["login_url"])

        code_result = await login_endpoint_queue.get()

        try:
            access_token = get_access_token(code_result, login_result['code_verifier'], login_result['redirect_uri'])
        except Exception as e:
            rprint(f'Error getting access token: {e}')
            continue

        rprint('Successfully logged in to bibox')

        await server.shutdown()
        webserver_task.cancel()

        return access_token
