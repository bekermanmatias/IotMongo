"""
Script con consultas de ejemplo para analizar datos IoT almacenados en MongoDB.
Incluye consultas básicas y agregaciones complejas.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import List, Dict, Any


class IoTQueries:
    """Clase para ejecutar consultas sobre datos IoT en MongoDB."""
    
    def __init__(self, mongo_uri: str, database_name: str = "iot_data", collection_name: str = "sensor_readings"):
        """
        Inicializa el cliente MongoDB para consultas.
        
        Args:
            mongo_uri: String de conexión a MongoDB Atlas.
            database_name: Nombre de la base de datos.
            collection_name: Nombre de la colección.
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.collection = None
    
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000
            )
            self.client.admin.command('ping')
            self.collection = self.client[self.database_name][self.collection_name]
            print("✓ Conexión establecida\n")
            return True
        except ConnectionFailure as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def get_last_n_readings(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los últimos N registros ordenados por timestamp.
        
        Args:
            n: Número de registros a obtener (default: 10).
        
        Returns:
            Lista de documentos.
        """
        if self.collection is None:
            return []
        
        try:
            results = list(
                self.collection.find()
                .sort("timestamp", -1)
                .limit(n)
            )
            return results
        except Exception as e:
            print(f"Error en consulta: {e}")
            return []
    
    def get_average_temperature_by_type(self) -> List[Dict[str, Any]]:
        """
        Calcula el promedio de temperatura por tipo de sensor usando agregación.
        Convierte temperaturas en Fahrenheit a Celsius para comparación.
        
        Returns:
            Lista con promedios agrupados por tipo.
        """
        if self.collection is None:
            return []
        
        try:
            pipeline = [
                {
                    "$project": {
                        "type": 1,
                        "temperature_celsius": {
                            "$cond": {
                                "if": {"$eq": ["$unit", "F"]},
                                "then": {
                                    "$subtract": [
                                        {"$divide": [{"$subtract": ["$temperature", 32]}, 1.8]},
                                        0
                                    ]
                                },
                                "else": "$temperature"
                            }
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$type",
                        "average_temperature": {"$avg": "$temperature_celsius"},
                        "count": {"$sum": 1},
                        "min_temperature": {"$min": "$temperature_celsius"},
                        "max_temperature": {"$max": "$temperature_celsius"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "sensor_type": "$_id",
                        "average_temperature_celsius": {"$round": ["$average_temperature", 2]},
                        "min_temperature_celsius": {"$round": ["$min_temperature", 2]},
                        "max_temperature_celsius": {"$round": ["$max_temperature", 2]},
                        "total_readings": "$count"
                    }
                },
                {
                    "$sort": {"sensor_type": 1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error en agregación: {e}")
            return []
    
    def filter_exterior_sensors(self) -> List[Dict[str, Any]]:
        """
        Filtra y obtiene solo los registros de sensores exteriores.
        
        Returns:
            Lista de documentos de sensores exteriores.
        """
        if self.collection is None:
            return []
        
        try:
            results = list(
                self.collection.find({"type": "exterior"})
                .sort("timestamp", -1)
            )
            return results
        except Exception as e:
            print(f"Error en consulta: {e}")
            return []
    
    def get_readings_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las lecturas de una ubicación específica.
        
        Args:
            location: Nombre de la ubicación.
        
        Returns:
            Lista de documentos.
        """
        if self.collection is None:
            return []
        
        try:
            results = list(
                self.collection.find({"location": location})
                .sort("timestamp", -1)
            )
            return results
        except Exception as e:
            print(f"Error en consulta: {e}")
            return []
    
    def get_readings_count_by_sensor(self) -> List[Dict[str, Any]]:
        """
        Cuenta el número de lecturas por sensor.
        
        Returns:
            Lista con conteos agrupados por device_id.
        """
        if self.collection is None:
            return []
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$device_id",
                        "count": {"$sum": 1},
                        "type": {"$first": "$type"},
                        "location": {"$first": "$location"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "device_id": "$_id",
                        "readings_count": "$count",
                        "sensor_type": "$type",
                        "location": "$location"
                    }
                },
                {
                    "$sort": {"readings_count": -1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error en agregación: {e}")
            return []
    
    def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()


def print_readings(readings: List[Dict[str, Any]], title: str = "Resultados"):
    """Función auxiliar para imprimir lecturas de forma legible."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    
    if not readings:
        print("No se encontraron registros.")
        return
    
    print(f"Total de registros: {len(readings)}\n")
    
    for i, reading in enumerate(readings[:5], 1):  # Mostrar solo los primeros 5
        print(f"Registro {i}:")
        for key, value in reading.items():
            if key != "_id":  # Omitir ObjectId para legibilidad
                print(f"  {key}: {value}")
        print()
    
    if len(readings) > 5:
        print(f"... y {len(readings) - 5} registros más\n")


def main():
    """Función principal para ejecutar consultas de ejemplo."""
    # Obtener URI de MongoDB
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )
    
    queries = IoTQueries(mongo_uri)
    
    if not queries.connect():
        print("No se pudo establecer conexión.")
        return
    
    try:
        # Consulta 1: Últimos 10 registros
        print("\n[CONSULTA 1] Últimos 10 registros")
        last_readings = queries.get_last_n_readings(10)
        print_readings(last_readings, "Últimos 10 registros")
        
        # Consulta 2: Promedio de temperatura por tipo
        print("\n[CONSULTA 2] Promedio de temperatura por tipo de sensor")
        avg_temps = queries.get_average_temperature_by_type()
        if avg_temps:
            print("\nResultados de agregación:")
            for result in avg_temps:
                print(f"  Tipo: {result['sensor_type']}")
                print(f"    Promedio: {result['average_temperature_celsius']}°C")
                print(f"    Mínimo: {result['min_temperature_celsius']}°C")
                print(f"    Máximo: {result['max_temperature_celsius']}°C")
                print(f"    Total lecturas: {result['total_readings']}")
                print()
        
        # Consulta 3: Filtrar sensores exteriores
        print("\n[CONSULTA 3] Sensores exteriores")
        exterior_readings = queries.filter_exterior_sensors()
        print_readings(exterior_readings, "Sensores exteriores")
        
        # Consulta adicional: Conteo por sensor
        print("\n[CONSULTA ADICIONAL] Conteo de lecturas por sensor")
        sensor_counts = queries.get_readings_count_by_sensor()
        if sensor_counts:
            print("\nConteo por dispositivo:")
            for result in sensor_counts:
                print(f"  {result['device_id']} ({result['sensor_type']}) - {result['location']}: {result['readings_count']} lecturas")
            print()
    
    finally:
        queries.close()


if __name__ == "__main__":
    main()

