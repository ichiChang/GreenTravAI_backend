# services/storage.py
from google.cloud import storage


def upload_image_to_gcs(file_stream, filename, content_type):
    client = storage.Client()
    bucket = client.bucket("ecotripbucket")
    blob = bucket.blob(filename)
    blob.upload_from_string(file_stream, content_type=content_type)
    return blob.public_url
