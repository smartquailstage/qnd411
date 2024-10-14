import os
from django.conf import settings

# Configuración de AWS
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400", 
    "ACL": "public-read"
}

# Configuración de almacenamiento
AWS_LOCATION = os.environ.get("AWS_LOCATION")  # Puede ser 'static' para archivos estáticos y 'media' para archivos de medios

# Almacenamiento de archivos estáticos
STATICFILES_STORAGE = os.environ.get("STATICFILES_STORAGE")
STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/'

# Almacenamiento de archivos de medios
DEFAULT_FILE_STORAGE = os.environ.get("DEFAULT_FILE_STORAGE")
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/media/'


# Opcional: Asegúrate de que los archivos de medios sean privados si es necesario
# MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'