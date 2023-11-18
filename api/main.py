#!/usr/bin/env python

import os
import json
import redis
from flask import Flask, request, jsonify
from flask_cors import CORS , cross_origin
import pandas as pd
from linkextractor import columnas
import numpy as np
from scipy.spatial.distance import cityblock


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

        col1 = data.get('col1')
        col2 = data.get('col2')
        col3 = data.get('col3')

        peli = pd.DataFrame(nombre)


        peli[col3] = pd.to_numeric(peli[col3], errors='coerce')
        #peli['movieId'] = pd.to_numeric(peli['movieId'], errors='coerce')
        peli[col1] = pd.to_numeric(peli[col1], errors='coerce')

        '''def consolidate_data2(df , a1 ,a2 ,x):
            consolidated_df1 = df.groupby([a1, a2])[x].mean().unstack()
            return consolidated_df1
        consolidated_dfmi = consolidate_data2(peli, col1, col2, col3)
        consolidated_dfmi = consolidated_dfmi.fillna(0)'''

        consolidated_dfmi = columnas(peli, col1, col2, col3)
        consolidated_dfmi = consolidated_dfmi.fillna(0)


        def computeNearestNeighbor(dataframe, target_user, distance_metric=cityblock):
            distances = np.zeros(len(dataframe))  # Initialize a NumPy array
            # Iterate over each row (user) in the DataFrame
            for i, (index, row) in enumerate(dataframe.iterrows()):
                if index == target_user:
                    continue  # Skip the target user itself
                # Calculate the distance between the target user and the current user
                distance = distance_metric(dataframe.loc[target_user], row)
                distances[i] = distance
            
            sorted_indices = np.argsort(distances)
            sorted_distances = distances[sorted_indices]
            return list(zip(dataframe.index[sorted_indices], sorted_distances))
        # Example usage
        # Assuming your DataFrame is named 'ratings_df'
        target_user_id = 1
        neighborsmi = computeNearestNeighbor(consolidated_dfmi, target_user_id)
        diccionario_resultante = dict(neighborsmi)
        valoresfinal = diccionario_resultante

        '''peli = pd.DataFrame(nombre)
        data = peli['rating'].value_counts().sort_index(ascending=False)
        diccionario_resultante = data.to_dict()
        valoresfinal = diccionario_resultante'''

        redis_conn.set('valoresfinal', json.dumps(valoresfinal))


        return jsonify(valoresfinal)
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
