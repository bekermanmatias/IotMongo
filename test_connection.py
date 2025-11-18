"""
Script de prueba rápida para verificar la conexión a MongoDB Atlas.
Útil para diagnosticar problemas de conexión antes de ejecutar los scripts principales.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError


def test_connection():
    """Prueba la conexión a MongoDB Atlas con mensajes detallados."""
    
    # Obtener URI de MongoDB
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )
    
    print("="*80)
    print("PRUEBA DE CONEXIÓN A MONGODB ATLAS")
    print("="*80)
    print(f"\nURI configurada: {mongo_uri[:50]}...")  # Mostrar solo primeros 50 caracteres por seguridad
    
    if "usuario:password" in mongo_uri:
        print("\n[ADVERTENCIA] Parece que esta usando la URI de ejemplo.")
        print("   Configure la variable de entorno MONGO_URI con su string real.\n")
    
    print("\n[1] Intentando conectar a MongoDB Atlas...")
    
    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000  # 10 segundos de timeout
        )
        
        print("   [OK] Cliente MongoDB creado")
        
        # Probar conexión
        print("\n[2] Verificando conexion (ping)...")
        client.admin.command('ping')
        print("   [OK] Conexion exitosa!")
        
        # Listar bases de datos
        print("\n[3] Listando bases de datos disponibles...")
        db_list = client.list_database_names()
        print(f"   [OK] Bases de datos encontradas: {len(db_list)}")
        for db in db_list[:5]:  # Mostrar solo las primeras 5
            print(f"      - {db}")
        if len(db_list) > 5:
            print(f"      ... y {len(db_list) - 5} mas")
        
        # Verificar base de datos iot_data
        print("\n[4] Verificando base de datos 'iot_data'...")
        db = client["iot_data"]
        if "iot_data" in db_list:
            print("   [OK] Base de datos 'iot_data' existe")
        else:
            print("   [INFO] Base de datos 'iot_data' no existe (se creara automaticamente)")
        
        # Verificar colección
        print("\n[5] Verificando coleccion 'sensor_readings'...")
        collection = db["sensor_readings"]
        count = collection.count_documents({})
        print(f"   [OK] Coleccion 'sensor_readings' accesible")
        print(f"   [OK] Documentos en la coleccion: {count}")
        
        if count == 0:
            print("\n   [INFO] La coleccion esta vacia.")
            print("   -> Ejecute 'python send_to_mongo.py' para generar datos primero.")
        else:
            print("\n   [OK] Hay datos en la coleccion. Puede proceder con las consultas.")
            # Mostrar un ejemplo
            sample = collection.find_one()
            if sample:
                print("\n   Ejemplo de documento:")
                for key, value in list(sample.items())[:5]:  # Primeros 5 campos
                    if key != "_id":
                        print(f"      {key}: {value}")
        
        # Probar inserción de prueba
        print("\n[6] Probando insercion de un documento de prueba...")
        test_doc = {
            "test": True,
            "timestamp": "2025-01-15T00:00:00Z"
        }
        result = collection.insert_one(test_doc)
        if result.inserted_id:
            print(f"   [OK] Insercion exitosa (ID: {result.inserted_id})")
            # Eliminar el documento de prueba
            collection.delete_one({"_id": result.inserted_id})
            print("   [OK] Documento de prueba eliminado")
        
        print("\n" + "="*80)
        print("[OK] TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("="*80)
        print("\nSu conexión a MongoDB Atlas está funcionando correctamente.")
        print("Puede proceder a ejecutar los scripts principales:")
        print("  - python send_to_mongo.py")
        print("  - python queries.py")
        print("  - python metrics.py")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"\n[ERROR] Timeout al conectar con MongoDB Atlas")
        print(f"   Detalles: {e}")
        print("\nPosibles causas:")
        print("  1. Su IP no esta en la whitelist de MongoDB Atlas")
        print("  2. Problemas de red/firewall")
        print("  3. El cluster de MongoDB esta inactivo")
        print("\nSolucion:")
        print("  - Vaya a MongoDB Atlas -> Network Access -> Add IP Address")
        print("  - Agregue su IP actual o use 0.0.0.0/0 (solo para desarrollo)")
        return False
        
    except ConfigurationError as e:
        print(f"\n[ERROR] URI de MongoDB mal formada")
        print(f"   Detalles: {e}")
        print("\nSolucion:")
        print("  - Verifique que la URI tenga el formato correcto:")
        print("    mongodb+srv://usuario:password@cluster.mongodb.net/...")
        return False
        
    except ConnectionFailure as e:
        print(f"\n[ERROR] Fallo de conexion")
        print(f"   Detalles: {e}")
        print("\nPosibles causas:")
        print("  1. Credenciales incorrectas (usuario/contrasena)")
        print("  2. El usuario no tiene permisos")
        print("  3. Problemas de red")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        print("\nDetalles completos:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_connection()

