import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam import window
import json
from google.cloud import storage
from apache_beam.io.gcp.pubsub import PubsubMessage 


class ReadFromGCS(beam.DoFn):
    def process(self, element):
        # The element is now a PubsubMessage object.
        # Access the payload via element.data
        if isinstance(element, PubsubMessage):
            payload = element.data
        else:
            # Fallback for older versions or if with_attributes=False is used
            payload = element

        # Decode the payload
        data = json.loads(payload.decode('utf-8'))
        
        # The rest of your code remains the same
        client = storage.Client()
        bucket_name = data['bucket']
        object_name = data['name']
        station_id = object_name.split('/')[1]
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        content = blob.download_as_string()
        
        parsed_data = json.loads(content)
        parsed_data['station_id'] = station_id
        
        yield parsed_data

class FlattenJsonData(beam.DoFn):
    def process(self, element):
        data_dict = element.get('data', {})
        iaqi_dict = data_dict.get('iaqi', {})
        city_dict = data_dict.get('city', {})
        time_dict = data_dict.get('time', {})
        
        flat_record = {
            'station_id': element.get('station_id'),
            'aqi': data_dict.get('aqi'),
            'dominentpol': data_dict.get('dominentpol'),
            'city_name': city_dict.get('name'),
            'measured_at': time_dict.get('iso'),
            'co': iaqi_dict.get('co', {}).get('v'),
            'dew': iaqi_dict.get('dew', {}).get('v'),
            'h': iaqi_dict.get('h', {}).get('v'),
            'no2': iaqi_dict.get('no2', {}).get('v'),
            'o3': iaqi_dict.get('o3', {}).get('v'),
            'p': iaqi_dict.get('p', {}).get('v'),
            'pm10': iaqi_dict.get('pm10', {}).get('v'),
            'pm25': iaqi_dict.get('pm25', {}).get('v'),
            'r': iaqi_dict.get('r', {}).get('v'),
            'so2': iaqi_dict.get('so2', {}).get('v'),
            't': iaqi_dict.get('t', {}).get('v'),
            'w': iaqi_dict.get('w', {}).get('v'),
            'wd': iaqi_dict.get('wd', {}).get('v'), # Se incluye 'wd' que puede faltar
            'wg': iaqi_dict.get('wg', {}).get('v'),
        }
        
        if flat_record.get('aqi') is not None:
            yield flat_record

def run_pipeline():
    options = PipelineOptions(
        runner='DataflowRunner',
        project='bigdatayandres',
        region='us-east1',
        staging_location='gs://dbyandres/staging',
        temp_location='gs://dbyandres/temp',
        job_name='aqi-ingestion',
        setup_file='./setup.py',
        streaming=True # Add this option for streaming pipelines
    )

    schema_string = 'station_id:STRING, aqi:INTEGER, dominentpol:STRING, city_name:STRING, measured_at:TIMESTAMP, co:FLOAT, dew:FLOAT, h:FLOAT, no2:FLOAT, o3:FLOAT, p:FLOAT, pm10:FLOAT, pm25:FLOAT, r:FLOAT, so2:FLOAT, t:FLOAT, w:FLOAT, wd:FLOAT, wg:FLOAT'

    with beam.Pipeline(options=options) as p:
        (p
         | 'Read from PubSub' >> beam.io.ReadFromPubSub(
             topic='projects/bigdatayandres/topics/aqi-notifications',
             with_attributes=True)
         | 'Read JSON from GCS' >> beam.ParDo(ReadFromGCS())
         | 'Flatten Data' >> beam.ParDo(FlattenJsonData())
         # This is the new part for windowing.
         # It groups elements into 5-minute windows
         | 'Windowing' >> beam.WindowInto(FixedWindows(60))
         | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
             table='bigdatayandres:your_dataset.aqi_data',
             schema=schema_string,
             write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
         )
        )

if __name__ == '__main__':
    run_pipeline()