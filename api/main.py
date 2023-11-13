#!/usr/bin/env python

import os
import json
import redis
from flask import Flask, request, jsonify
from flask_cors import CORS , cross_origin
import pandas as pd

app = Flask(__name__)
CORS(app)

redis_conn = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

@app.route("/")
def index():
    return "Usage: http://<hostname>[:<prt>]/api/<url>"

#----------------------------------------------------------------
total = {}
valoresfinal = {}

@app.route('/api/valor', methods=['POST'])
def recibir_datos():
    global valoresfinal
    if request.method == 'POST':
        data = request.get_json()  
        nombre = data.get('obj')  

        peli = pd.DataFrame(nombre)
        data = peli['rating'].value_counts().sort_index(ascending=False)
        diccionario_resultante = data.to_dict()
        valoresfinal = diccionario_resultante


        '''total.update(nombre)
        valores = pd.DataFrame(total)
        valores = valores.fillna(0)

        def coseno(name):
            dot_product = 0
            magnitude_a = 0
            magnitude_b = 0
            suma = 0
            for index , row in valores.iterrows():
                suma += 1
                if (row.Angelica ==  0 or row[name] == 0 ):
                    dot_product = dot_product
            
                else :
                    dot_product += row.Angelica  * row[name]
                    magnitude_a += row.Angelica  ** 2
                    magnitude_b += row[name]  ** 2
            magnitude_a = magnitude_a ** 0.5 
            magnitude_b = magnitude_b ** 0.5
            #print(suma)
            cosine_similarity = dot_product / (magnitude_a * magnitude_b)
            return cosine_similarity

        nombres = [columna for columna in valores.columns if columna not in ["Unnamed: 0", "Angelica"]]
        
        for x in nombres:
            r = coseno(x)  
            valoresfinal[x] = r
              # Almacena los valores finales en Redis'''
        redis_conn.set('valoresfinal', json.dumps(valoresfinal))


        return jsonify(nombre)
    else:
        return jsonify({"mensaje": "Esta ruta solo acepta solicitudes POST"})
#----------------------------------------------------------------



@app.route('/api/valor', methods=['GET'])
def get_users():
    # Intenta recuperar datos desde Redis
    cached_data = redis_conn.get('valoresfinal') 
    if cached_data:
        return jsonify(json.loads(cached_data))
    else:
        return jsonify({"mensaje": "No hay valores finales almacenados en Redis"})


app.run(host="0.0.0.0")
