"""
Scripts opcionales para análisis avanzado de datos IoT.
Incluye análisis de promedios por hora, conteo de lecturas y detección de valores atípicos.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics


class AdvancedAnalysis:
    """Clase para realizar análisis avanzados sobre datos IoT."""
    
    def __init__(self, mongo_uri: str, database_name: str = "iot_data", collection_name: str = "sensor_readings"):
        """
        Inicializa el analizador avanzado.
        
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
        """Establece conexión con MongoDB."""
        try:
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000
            )
            self.client.admin.command('ping')
            self.collection = self.client[self.database_name][self.collection_name]
            return True
        except ConnectionFailure as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def average_temperature_by_hour(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Calcula el promedio de temperatura por hora para las últimas N horas.
        
        Args:
            hours_back: Número de horas hacia atrás a analizar (default: 24).
        
        Returns:
            Lista con promedios agrupados por hora.
        """
        if self.collection is None:
            return []
        
        try:
            # Calcular timestamp de inicio
            start_time = datetime.now() - timedelta(hours=hours_back)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_time.isoformat()
                        }
                    }
                },
                {
                    "$project": {
                        "hour": {
                            "$hour": {
                                "$dateFromString": {
                                    "dateString": "$timestamp"
                                }
                            }
                        },
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
                        },
                        "type": 1
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "hour": "$hour",
                            "type": "$type"
                        },
                        "average_temperature": {"$avg": "$temperature_celsius"},
                        "count": {"$sum": 1},
                        "min_temp": {"$min": "$temperature_celsius"},
                        "max_temp": {"$max": "$temperature_celsius"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "hour": "$_id.hour",
                        "sensor_type": "$_id.type",
                        "average_temperature_celsius": {"$round": ["$average_temperature", 2]},
                        "min_temperature_celsius": {"$round": ["$min_temp", 2]},
                        "max_temperature_celsius": {"$round": ["$max_temp", 2]},
                        "readings_count": "$count"
                    }
                },
                {
                    "$sort": {"hour": 1, "sensor_type": 1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error en análisis por hora: {e}")
            return []
    
    def count_readings_by_sensor(self) -> List[Dict[str, Any]]:
        """
        Cuenta el número total de lecturas por cada sensor.
        
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
                        "total_readings": {"$sum": 1},
                        "sensor_type": {"$first": "$type"},
                        "location": {"$first": "$location"},
                        "first_reading": {"$min": "$timestamp"},
                        "last_reading": {"$max": "$timestamp"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "device_id": "$_id",
                        "total_readings": 1,
                        "sensor_type": 1,
                        "location": 1,
                        "first_reading": 1,
                        "last_reading": 1
                    }
                },
                {
                    "$sort": {"total_readings": -1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error en conteo por sensor: {e}")
            return []
    
    def detect_outliers(self, field: str = "temperature", z_threshold: float = 2.5) -> List[Dict[str, Any]]:
        """
        Detecta valores atípicos usando el método de puntuación Z.
        
        Args:
            field: Campo numérico a analizar (default: "temperature").
            z_threshold: Umbral de desviación estándar para considerar outlier (default: 2.5).
        
        Returns:
            Lista de documentos identificados como outliers.
        """
        if self.collection is None:
            return []
        
        try:
            # Primero, obtener todos los valores y calcular estadísticas
            all_readings = list(self.collection.find({}, {field: 1, "device_id": 1, "type": 1, "timestamp": 1, "unit": 1}))
            
            if not all_readings:
                return []
            
            # Convertir temperaturas a Celsius para análisis consistente
            values = []
            for reading in all_readings:
                if field in reading:
                    if field == "temperature" and reading.get("unit") == "F":
                        # Convertir Fahrenheit a Celsius
                        value = (reading[field] - 32) / 1.8
                    else:
                        value = reading[field]
                    values.append(value)
            
            if len(values) < 2:
                return []
            
            # Calcular media y desviación estándar
            mean = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            if std_dev == 0:
                return []
            
            # Identificar outliers
            outliers = []
            for reading in all_readings:
                if field in reading:
                    if field == "temperature" and reading.get("unit") == "F":
                        value = (reading[field] - 32) / 1.8
                    else:
                        value = reading[field]
                    
                    z_score = abs((value - mean) / std_dev)
                    
                    if z_score > z_threshold:
                        outlier_doc = {
                            "device_id": reading.get("device_id"),
                            "type": reading.get("type"),
                            "timestamp": reading.get("timestamp"),
                            field: reading[field],
                            "unit": reading.get("unit"),
                            "z_score": round(z_score, 3),
                            "value_celsius": round(value, 2) if field == "temperature" else value,
                            "mean": round(mean, 2),
                            "std_dev": round(std_dev, 2)
                        }
                        outliers.append(outlier_doc)
            
            # Ordenar por z_score descendente
            outliers.sort(key=lambda x: x["z_score"], reverse=True)
            return outliers
        
        except Exception as e:
            print(f"Error en detección de outliers: {e}")
            return []
    
    def print_hourly_averages(self, results: List[Dict[str, Any]]):
        """Imprime los promedios por hora de forma legible."""
        if not results:
            print("No hay datos para mostrar.")
            return
        
        print("\n" + "="*80)
        print("PROMEDIO DE TEMPERATURA POR HORA")
        print("="*80)
        
        current_hour = None
        for result in results:
            hour = result["hour"]
            if hour != current_hour:
                if current_hour is not None:
                    print()
                print(f"\nHora {hour:02d}:00")
                current_hour = hour
            
            print(f"  Tipo: {result['sensor_type']}")
            print(f"    Promedio: {result['average_temperature_celsius']}°C")
            print(f"    Rango: {result['min_temperature_celsius']}°C - {result['max_temperature_celsius']}°C")
            print(f"    Lecturas: {result['readings_count']}")
    
    def print_sensor_counts(self, results: List[Dict[str, Any]]):
        """Imprime los conteos por sensor de forma legible."""
        if not results:
            print("No hay datos para mostrar.")
            return
        
        print("\n" + "="*80)
        print("CONTEO DE LECTURAS POR SENSOR")
        print("="*80)
        
        total = sum(r["total_readings"] for r in results)
        print(f"\nTotal de lecturas en la base de datos: {total}\n")
        
        for result in results:
            percentage = (result["total_readings"] / total * 100) if total > 0 else 0
            print(f"  {result['device_id']} ({result['sensor_type']}) - {result['location']}")
            print(f"    Total: {result['total_readings']} lecturas ({percentage:.1f}%)")
            print(f"    Primera lectura: {result['first_reading']}")
            print(f"    Última lectura: {result['last_reading']}")
            print()
    
    def print_outliers(self, outliers: List[Dict[str, Any]], field: str = "temperature"):
        """Imprime los valores atípicos de forma legible."""
        if not outliers:
            print("No se detectaron valores atípicos.")
            return
        
        print("\n" + "="*80)
        print(f"VALORES ATÍPICOS DETECTADOS - Campo: {field}")
        print("="*80)
        print(f"\nTotal de outliers: {len(outliers)}\n")
        
        for i, outlier in enumerate(outliers[:10], 1):  # Mostrar solo los primeros 10
            print(f"Outlier #{i}:")
            print(f"  Device ID: {outlier['device_id']}")
            print(f"  Tipo: {outlier['type']}")
            print(f"  Timestamp: {outlier['timestamp']}")
            print(f"  Valor original: {outlier[field]} {outlier.get('unit', '')}")
            if field == "temperature":
                print(f"  Valor en Celsius: {outlier['value_celsius']}°C")
            print(f"  Z-score: {outlier['z_score']}")
            print(f"  Media: {outlier['mean']}")
            print(f"  Desviación estándar: {outlier['std_dev']}")
            print()
        
        if len(outliers) > 10:
            print(f"... y {len(outliers) - 10} outliers más\n")
    
    def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()


def main():
    """Función principal para ejecutar análisis avanzados."""
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )
    
    analyzer = AdvancedAnalysis(mongo_uri)
    
    if not analyzer.connect():
        print("No se pudo establecer conexión.")
        return
    
    try:
        # Análisis 1: Promedio por hora
        print("\n[ANÁLISIS 1] Promedio de temperatura por hora (últimas 24 horas)")
        hourly_avg = analyzer.average_temperature_by_hour(hours_back=24)
        analyzer.print_hourly_averages(hourly_avg)
        
        # Análisis 2: Conteo por sensor
        print("\n[ANÁLISIS 2] Conteo de lecturas por sensor")
        sensor_counts = analyzer.count_readings_by_sensor()
        analyzer.print_sensor_counts(sensor_counts)
        
        # Análisis 3: Detección de outliers
        print("\n[ANÁLISIS 3] Detección de valores atípicos (temperatura)")
        outliers = analyzer.detect_outliers(field="temperature", z_threshold=2.5)
        analyzer.print_outliers(outliers, field="temperature")
    
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()

