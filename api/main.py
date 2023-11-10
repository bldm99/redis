#!/usr/bin/env python

import os
import json
import redis
from flask import Flask, request, jsonify
from linkextractor import extract_links

app = Flask(__name__)
redis_conn = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

@app.route("/")
def index():
    return "Usage: http://<hostname>[:<prt>]/api/<url>"



@app.route('/api/valor', methods=['GET'])
def get_users():
    # Intenta recuperar datos desde Redis
    cached_data = redis_conn.get('cached_data')
    if cached_data:
        return jsonify(json.loads(cached_data))

    # Si no hay datos en Redis, genera los datos y almacénalos en Redis
    users_data = extract_links()

    # Almacena los datos en Redis con una clave y un tiempo de vencimiento (por ejemplo, 3600 segundos)
    redis_conn.set('cached_data', json.dumps(users_data), ex=3600)

    return jsonify(users_data)



app.run(host="0.0.0.0")
