import pandas as pd
import time
import json
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient

FILE_PATH = 'faa_sdr_data.xls' 

CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

CONTAINER_NAME = 'raw-logs'

def stream_logs():
    if not CONNECTION_STRING:
        print("ERROR: Azure Connection String is missing!")
        return

    print(f"Loading HTML dataset from {FILE_PATH}...")
    try:
        df = pd.read_html(FILE_PATH)[0]
        df = df.dropna(how='all')
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print("Connecting to Azure Blob Storage...")
    
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    print("Success! Starting simulated log stream to the Cloud...\n")
    
    while True:
        sample = df.sample(n=2)
        batch_data = [] # Create an empty list to hold our 2 logs
        
        for index, row in sample.iterrows():
            record = row.dropna().to_dict()
            record["stream_timestamp"] = datetime.utcnow().isoformat() + "Z"
            batch_data.append(record) # Add the log to our batch
            
        # 1. Convert the batch into a formatted JSON string
        json_output = json.dumps(batch_data, indent=2)
        
        # 2. Create a unique filename using the current exact time
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_name = f"maintenance_logs_{timestamp_str}.json"
        
        # 3. Upload the file to Azure 'raw-logs' folder
        try:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
            blob_client.upload_blob(json_output, overwrite=True)
            print(f"Successfully beamed to cloud: {blob_name}")
        except Exception as e:
            print(f"Failed to upload to Azure: {e}")
            
        print("Waiting 10 seconds for the next batch...\n")
        time.sleep(10)

if __name__ == "__main__":
    stream_logs()