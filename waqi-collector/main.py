import os
import requests
import json
from datetime import datetime
from google.cloud import storage, secretmanager
from flask import Flask, request

app = Flask(__name__)

def get_secret(secret_id, project_id):
    """Obtiene un secreto de Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@app.route("/", methods=["GET"])
def run_job():
    """Endpoint que ejecuta la tarea."""
    project_id = os.environ.get('GCP_PROJECT_ID', 'bigdatayandres')
    secret_id = "waqi_api"
    bucket_name = "dbyandres"
    base_folder = "waqi"
    
    try:
        aqi_token = get_secret(secret_id, project_id)
        station_uids = ["H6234", "H6240", "H6230", "H6232", "H6231", "H6233", "H8512", "H6235"]
        base_url = "https://api.waqi.info/feed/@{}/?token={}"
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        current_datetime = datetime.now()
        datetime_str = current_datetime.strftime("%Y%m%d%H")

        for uid in station_uids:
            try:
                response = requests.get(base_url.format(uid, aqi_token))
                response.raise_for_status()
                data = response.json()
                
                file_path = f"{base_folder}/{uid}/{datetime_str}.json"
                
                blob = bucket.blob(file_path)
                blob.upload_from_string(
                    data=json.dumps(data),
                    content_type="application/json"
                )
                
                print(f"Datos de la estación {uid} guardados en: {file_path}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener datos para la estación {uid}: {e}")
        
        return "Job completed successfully!", 200
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Job failed with error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))