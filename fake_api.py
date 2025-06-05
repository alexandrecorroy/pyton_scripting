from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Optional
from dotenv import load_dotenv
import random
import time
import os

load_dotenv()

app = FastAPI()

API_TOKEN = os.getenv('API_TOKEN')

@app.middleware('http')
async def check_token(request: Request, call_next):
  auth = request.headers.get('Authorization')
  if request.url.path == "/login":
    return await call_next(request)
  if not auth or auth != f'Bearer {API_TOKEN}':
    return JSONResponse(status_code=401, content='Unauthorized: Invalid or missing token')
  return await call_next(request)

@app.get('/status')
def get_status(app: Optional[str] = 'unknown'):
  fake_response_time = round(random.uniform(0.1, 1.5), 2)
  status = random.choice(['OK', 'DEGRADED', 'DOWN'])
  time.sleep(0.5)

  return JSONResponse(content={
    'app': app,
    'status': status,
    'response_time': fake_response_time,
    'timestamp': time.time()
  })

@app.post('/login')
async def get_token(request: Request):

  login = request.headers.get('login')
  password = request.headers.get('password')

  if(login != '' and password != ''):
    fake_response_time = round(random.uniform(0.1, 1.5), 2)
    time.sleep(0.5)

    return JSONResponse(
      status_code=200,
      content={
      'token': API_TOKEN,
      'response_time': fake_response_time
    })
  else:
    return JSONResponse(status_code=401, content='Unauthorized: Invalid login or password')