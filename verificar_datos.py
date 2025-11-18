"""
Script rápido para verificar cuántos datos hay en la base de datos.
"""

import os
from pymongo import MongoClient

# Obtener URI de MongoDB
mongo_uri = os.getenv(
    "MONGO_URI",
    "mongodb+srv://natashacadabon:Natasha1234@iotcluster.55iunlr.mongodb.net/?appName=IoTCluster"
)

try:
    print("Conectando a MongoDB Atlas...")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    
    db = client["iot_data"]
    collection = db["sensor_readings"]
    
    # Contar documentos
    count = collection.count_documents({})
    
    print(f"\n{'='*60}")
    print(f"ESTADO DE LA BASE DE DATOS")
    print(f"{'='*60}")
    print(f"\nBase de datos: iot_data")
    print(f"Coleccion: sensor_readings")
    print(f"\nTotal de documentos: {count}")
    
    if count > 0:
        print(f"\n[OK] Los datos ESTAN guardados en MongoDB Atlas!")
        
        # Mostrar algunos ejemplos
        print(f"\nEjemplos de documentos almacenados:")
        print(f"{'-'*60}")
        
        # Últimos 3 documentos
        latest = list(collection.find().sort("timestamp", -1).limit(3))
        for i, doc in enumerate(latest, 1):
            print(f"\nDocumento #{i}:")
            print(f"  device_id: {doc.get('device_id')}")
            print(f"  type: {doc.get('type')}")
            print(f"  location: {doc.get('location')}")
            if 'temperature' in doc:
                print(f"  temperature: {doc.get('temperature')}°{doc.get('unit', '')}")
            if 'humidity' in doc:
                print(f"  humidity: {doc.get('humidity')}%")
            if 'uv_index' in doc:
                print(f"  uv_index: {doc.get('uv_index')}")
            print(f"  timestamp: {doc.get('timestamp')}")
        
        # Estadísticas rápidas
        print(f"\n{'-'*60}")
        print(f"Estadisticas:")
        
        interior_count = collection.count_documents({"type": "interior"})
        exterior_count = collection.count_documents({"type": "exterior"})
        
        print(f"  Sensores interiores: {interior_count}")
        print(f"  Sensores exteriores: {exterior_count}")
        
        # Primer y último timestamp
        first = collection.find_one(sort=[("timestamp", 1)])
        last = collection.find_one(sort=[("timestamp", -1)])
        
        if first and last:
            print(f"\n  Primer registro: {first.get('timestamp')}")
            print(f"  Ultimo registro: {last.get('timestamp')}")
    else:
        print(f"\n[INFO] La coleccion esta vacia.")
        print(f"  Ejecuta 'python send_to_mongo.py' para generar datos.")
    
    print(f"\n{'='*60}")
    
    client.close()
    
except Exception as e:
    print(f"[ERROR] {e}")

