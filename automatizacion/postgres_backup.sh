#!/bin/bash

# Variables
BACKUP_DIR="/path/to/backup"
DATE=$(date +%Y%m%d%H%M%S)
BACKUP_FILE="backup_$DATE.sql"
CONTAINER_NAME="<postgres_container_name>"
DB_NAME="your_database_name"
USER="your_user"

# Crear copia de seguridad
docker exec $CONTAINER_NAME pg_dump -U $USER -d $DB_NAME -F c -b -v -f /tmp/$BACKUP_FILE

# Copiar el archivo de respaldo al host
docker cp $CONTAINER_NAME:/tmp/$BACKUP_FILE $BACKUP_DIR/$BACKUP_FILE

# Limpiar archivos temporales
docker exec $CONTAINER_NAME rm /tmp/$BACKUP_FILE

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"