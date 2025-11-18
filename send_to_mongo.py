"""
Script para enviar lecturas de sensores IoT a MongoDB Atlas.
Conecta con la base de datos y envía datos cada 5 segundos.
"""

import time
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from sensor_simulator import SensorSimulator
from datetime import datetime


class MongoSender:
    """Clase para gestionar el envío de datos a MongoDB Atlas."""
    
    def __init__(self, mongo_uri: str, database_name: str = "iot_data", collection_name: str = "sensor_readings"):
        """
        Inicializa el cliente MongoDB.
        
        Args:
            mongo_uri: String de conexión a MongoDB Atlas.
            database_name: Nombre de la base de datos.
            collection_name: Nombre de la colección.
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.simulator = SensorSimulator()
    
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB Atlas.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000  # Timeout de 5 segundos
            )
            # Verificar conexión
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Conexión establecida exitosamente")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Base de datos: {self.database_name}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Colección: {self.collection_name}\n")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error de conexión: {e}")
            return False
    
    def send_reading(self, reading: dict) -> bool:
        """
        Envía una lectura a MongoDB.
        
        Args:
            reading: Dict con la lectura del sensor.
        
        Returns:
            True si la inserción fue exitosa, False en caso contrario.
        """
        try:
            result = self.collection.insert_one(reading)
            return result.inserted_id is not None
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error al insertar: {e}")
            return False
    
    def run(self, interval: int = 5, max_readings: int = None):
        """
        Ejecuta el envío continuo de lecturas.
        
        Args:
            interval: Intervalo en segundos entre envíos (default: 5).
            max_readings: Número máximo de lecturas a enviar. None para ilimitado.
        """
        if not self.connect():
            print("No se pudo establecer conexión. Verifique la URI de MongoDB.")
            return
        
        count = 0
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando envío de lecturas (intervalo: {interval}s)\n")
        print("=" * 80)
        
        try:
            while True:
                # Generar lectura aleatoria
                reading = self.simulator.generate_random_reading()
                
                # Enviar a MongoDB
                success = self.send_reading(reading)
                
                if success:
                    count += 1
                    # Mostrar lectura enviada
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Lectura #{count} enviada:")
                    print(f"  Device ID: {reading['device_id']}")
                    print(f"  Tipo: {reading['type']}")
                    print(f"  Ubicación: {reading['location']}")
                    if 'temperature' in reading:
                        print(f"  Temperatura: {reading['temperature']}°{reading['unit']}")
                    if 'humidity' in reading:
                        print(f"  Humedad: {reading['humidity']}%")
                    if 'light' in reading:
                        print(f"  Luz: {reading['light']} lux")
                    if 'uv_index' in reading:
                        print(f"  Índice UV: {reading['uv_index']}")
                    print(f"  Timestamp: {reading['timestamp']}")
                    print("-" * 80)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error al enviar lectura")
                
                # Verificar límite
                if max_readings and count >= max_readings:
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Se alcanzó el límite de {max_readings} lecturas.")
                    break
                
                # Esperar antes de la siguiente lectura
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Proceso interrumpido por el usuario.")
        finally:
            if self.client:
                self.client.close()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Conexión cerrada.")


def main():
    """Función principal."""
    # Obtener URI de MongoDB desde variable de entorno o usar valor por defecto
    # IMPORTANTE: Reemplazar con tu URI real de MongoDB Atlas
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )
    
    if "usuario:password" in mongo_uri:
        print("⚠ ADVERTENCIA: Usando URI de ejemplo. Configure la variable de entorno MONGO_URI")
        print("   o modifique el código con su URI real de MongoDB Atlas.\n")
    
    sender = MongoSender(mongo_uri)
    
    # Ejecutar envío continuo (presionar Ctrl+C para detener)
    # Para pruebas, puede limitarse con max_readings=10
    sender.run(interval=5, max_readings=None)


if __name__ == "__main__":
    main()

