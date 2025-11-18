"""
Script para medir el rendimiento del sistema IoT-MongoDB.
Evalúa latencia de inserción, tiempo de ejecución de consultas y otras métricas.
"""

import time
import os
import statistics
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sensor_simulator import SensorSimulator
from typing import List, Dict, Any, Tuple


class PerformanceMetrics:
    """Clase para medir el rendimiento del sistema."""
    
    def __init__(self, mongo_uri: str, database_name: str = "iot_data", collection_name: str = "sensor_readings"):
        """
        Inicializa el medidor de rendimiento.
        
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
        self.simulator = SensorSimulator()
    
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            print("Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=10000  # Aumentado a 10 segundos
            )
            # Verificar conexión
            self.client.admin.command('ping')
            self.collection = self.client[self.database_name][self.collection_name]
            print("[OK] Conexion establecida exitosamente")
            
            # Verificar si hay datos en la colección
            count = self.collection.count_documents({})
            print(f"[OK] Coleccion '{self.collection_name}' encontrada con {count} documentos")
            if count == 0:
                print("[INFO] Advertencia: La coleccion esta vacia. Algunas metricas pueden no funcionar correctamente.")
            
            return True
        except ConnectionFailure as e:
            print(f"[ERROR] Error de conexion: {e}")
            print("  Verifique:")
            print("  - Que la URI de MongoDB sea correcta")
            print("  - Que su IP este en la whitelist de MongoDB Atlas")
            print("  - Que el usuario tenga permisos de lectura/escritura")
            return False
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            print(f"  Tipo de error: {type(e).__name__}")
            return False
    
    def measure_insertion_latency(self, num_inserts: int = 100) -> Dict[str, Any]:
        """
        Mide la latencia de inserción de documentos.
        
        Args:
            num_inserts: Número de inserciones a realizar para el test.
        
        Returns:
            Dict con métricas de latencia.
        """
        if self.collection is None:
            return {}
        
        latencies = []
        successful_inserts = 0
        failed_inserts = 0
        
        print(f"Mediendo latencia de inserción ({num_inserts} inserciones)...")
        
        for i in range(num_inserts):
            # Generar lectura
            reading = self.simulator.generate_random_reading()
            
            # Medir tiempo de inserción
            start_time = time.perf_counter()
            try:
                result = self.collection.insert_one(reading)
                end_time = time.perf_counter()
                
                if result.inserted_id:
                    latency_ms = (end_time - start_time) * 1000  # Convertir a milisegundos
                    latencies.append(latency_ms)
                    successful_inserts += 1
                else:
                    failed_inserts += 1
            except Exception as e:
                failed_inserts += 1
                if (i + 1) % 10 == 0:  # Solo mostrar cada 10 errores
                    print(f"  Error en insercion {i+1}: {e}")
        
        if not latencies:
            return {
                "successful_inserts": 0,
                "failed_inserts": failed_inserts,
                "error": "No se pudieron realizar inserciones exitosas"
            }
        
        metrics = {
            "total_inserts": num_inserts,
            "successful_inserts": successful_inserts,
            "failed_inserts": failed_inserts,
            "success_rate": (successful_inserts / num_inserts) * 100,
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "avg_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "std_deviation_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "p95_latency_ms": self._percentile(latencies, 95),
            "p99_latency_ms": self._percentile(latencies, 99)
        }
        
        return metrics
    
    def measure_query_performance(self) -> Dict[str, Any]:
        """
        Mide el tiempo de ejecución de diferentes consultas.
        
        Returns:
            Dict con métricas de rendimiento de consultas.
        """
        if self.collection is None:
            return {}
        
        results = {}
        
        # Verificar si hay datos
        total_docs = self.collection.count_documents({})
        if total_docs == 0:
            print("[INFO] Advertencia: No hay documentos en la coleccion. Las consultas no se ejecutaran.")
            return {}
        
        print("Midiendo rendimiento de consultas...")
        
        try:
            # Consulta 1: Últimos 10 registros
            start_time = time.perf_counter()
            last_10 = list(self.collection.find().sort("timestamp", -1).limit(10))
            end_time = time.perf_counter()
            results["last_10_readings"] = {
                "execution_time_ms": (end_time - start_time) * 1000,
                "results_count": len(last_10)
            }
        except Exception as e:
            print(f"  Error en consulta 'últimos 10 registros': {e}")
            results["last_10_readings"] = {
                "execution_time_ms": 0,
                "results_count": 0,
                "error": str(e)
            }
        
        try:
            # Consulta 2: Filtro por tipo
            start_time = time.perf_counter()
            exterior = list(self.collection.find({"type": "exterior"}))
            end_time = time.perf_counter()
            results["filter_exterior"] = {
                "execution_time_ms": (end_time - start_time) * 1000,
                "results_count": len(exterior)
            }
        except Exception as e:
            print(f"  Error en consulta 'filtro exterior': {e}")
            results["filter_exterior"] = {
                "execution_time_ms": 0,
                "results_count": 0,
                "error": str(e)
            }
        
        try:
            # Consulta 3: Agregación - promedio por tipo
            pipeline = [
                {
                    "$group": {
                        "_id": "$type",
                        "avg_temp": {"$avg": "$temperature"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            start_time = time.perf_counter()
            aggregation = list(self.collection.aggregate(pipeline))
            end_time = time.perf_counter()
            results["avg_temp_by_type"] = {
                "execution_time_ms": (end_time - start_time) * 1000,
                "results_count": len(aggregation)
            }
        except Exception as e:
            print(f"  Error en agregación 'promedio por tipo': {e}")
            results["avg_temp_by_type"] = {
                "execution_time_ms": 0,
                "results_count": 0,
                "error": str(e)
            }
        
        try:
            # Consulta 4: Conteo total
            start_time = time.perf_counter()
            total_count = self.collection.count_documents({})
            end_time = time.perf_counter()
            results["total_count"] = {
                "execution_time_ms": (end_time - start_time) * 1000,
                "results_count": total_count
            }
        except Exception as e:
            print(f"  Error en consulta 'conteo total': {e}")
            results["total_count"] = {
                "execution_time_ms": 0,
                "results_count": 0,
                "error": str(e)
            }
        
        return results
    
    def measure_throughput(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """
        Mide el throughput (inserciones por segundo) durante un período.
        
        Args:
            duration_seconds: Duración del test en segundos.
        
        Returns:
            Dict con métricas de throughput.
        """
        if self.collection is None:
            return {}
        
        print(f"Midiendo throughput durante {duration_seconds} segundos...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        insert_count = 0
        
        while time.time() < end_time:
            reading = self.simulator.generate_random_reading()
            try:
                self.collection.insert_one(reading)
                insert_count += 1
            except Exception:
                pass
        
        actual_duration = time.time() - start_time
        throughput = insert_count / actual_duration if actual_duration > 0 else 0
        
        return {
            "duration_seconds": actual_duration,
            "total_inserts": insert_count,
            "throughput_inserts_per_second": throughput
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calcula el percentil de una lista de valores.
        
        Args:
            data: Lista de valores numéricos.
            percentile: Percentil deseado (0-100).
        
        Returns:
            Valor del percentil.
        """
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_data):
            return sorted_data[-1]
        
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def print_metrics(self, insertion_metrics: Dict[str, Any], query_metrics: Dict[str, Any], throughput_metrics: Dict[str, Any]):
        """
        Imprime las métricas de forma legible.
        
        Args:
            insertion_metrics: Métricas de inserción.
            query_metrics: Métricas de consultas.
            throughput_metrics: Métricas de throughput.
        """
        print("\n" + "="*80)
        print("MÉTRICAS DE RENDIMIENTO - SISTEMA IoT-MongoDB")
        print("="*80)
        
        # Métricas de inserción
        if insertion_metrics and "error" not in insertion_metrics:
            print("\n[1] LATENCIA DE INSERCIÓN")
            print("-" * 80)
            print(f"  Total de inserciones: {insertion_metrics['total_inserts']}")
            print(f"  Exitosas: {insertion_metrics['successful_inserts']}")
            print(f"  Fallidas: {insertion_metrics['failed_inserts']}")
            print(f"  Tasa de éxito: {insertion_metrics['success_rate']:.2f}%")
            print(f"\n  Latencia mínima: {insertion_metrics['min_latency_ms']:.2f} ms")
            print(f"  Latencia máxima: {insertion_metrics['max_latency_ms']:.2f} ms")
            print(f"  Latencia promedio: {insertion_metrics['avg_latency_ms']:.2f} ms")
            print(f"  Latencia mediana: {insertion_metrics['median_latency_ms']:.2f} ms")
            print(f"  Desviación estándar: {insertion_metrics['std_deviation_ms']:.2f} ms")
            print(f"  Percentil 95: {insertion_metrics['p95_latency_ms']:.2f} ms")
            print(f"  Percentil 99: {insertion_metrics['p99_latency_ms']:.2f} ms")
        
        # Métricas de consultas
        if query_metrics:
            print("\n[2] RENDIMIENTO DE CONSULTAS")
            print("-" * 80)
            for query_name, metrics in query_metrics.items():
                print(f"  {query_name.replace('_', ' ').title()}:")
                if "error" in metrics:
                    print(f"    [ERROR] Error: {metrics['error']}")
                else:
                    print(f"    Tiempo de ejecución: {metrics['execution_time_ms']:.2f} ms")
                    print(f"    Registros obtenidos: {metrics['results_count']}")
        else:
            print("\n[2] RENDIMIENTO DE CONSULTAS")
            print("-" * 80)
            print("  No se pudieron ejecutar las consultas (colección vacía o error de conexión)")
        
        # Métricas de throughput
        if throughput_metrics:
            print("\n[3] THROUGHPUT")
            print("-" * 80)
            print(f"  Duración del test: {throughput_metrics['duration_seconds']:.2f} segundos")
            print(f"  Total de inserciones: {throughput_metrics['total_inserts']}")
            print(f"  Throughput: {throughput_metrics['throughput_inserts_per_second']:.2f} inserciones/segundo")
        
        print("\n" + "="*80)
    
    def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()


def main():
    """Función principal para ejecutar las métricas."""
    # Obtener URI de MongoDB
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    )
    
    if "usuario:password" in mongo_uri:
        print("[ADVERTENCIA] Usando URI de ejemplo.")
        print("   Configure la variable de entorno MONGO_URI con su string de conexion real.\n")
    
    metrics = PerformanceMetrics(mongo_uri)
    
    if not metrics.connect():
        print("\nNo se pudo establecer conexion.")
        print("\nSugerencias:")
        print("1. Verifique que la variable MONGO_URI este configurada correctamente")
        print("2. Asegurese de que su IP este en la whitelist de MongoDB Atlas")
        print("3. Verifique que el usuario tenga permisos de lectura/escritura")
        print("\nEjecute 'python test_connection.py' para diagnosticar el problema.")
        return
    
    try:
        print("\n" + "="*80)
        print("INICIANDO MEDICIÓN DE MÉTRICAS")
        print("="*80 + "\n")
        
        # Medir latencia de inserción
        print("[PASO 1/3] Midiendo latencia de inserción...")
        insertion_metrics = metrics.measure_insertion_latency(num_inserts=100)
        
        # Medir rendimiento de consultas
        print("\n[PASO 2/3] Midiendo rendimiento de consultas...")
        query_metrics = metrics.measure_query_performance()
        
        # Medir throughput
        print("\n[PASO 3/3] Midiendo throughput...")
        throughput_metrics = metrics.measure_throughput(duration_seconds=10)
        
        # Imprimir todas las métricas
        metrics.print_metrics(insertion_metrics, query_metrics, throughput_metrics)
    
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\n[ERROR] Error durante la ejecucion: {e}")
        print(f"  Tipo de error: {type(e).__name__}")
        import traceback
        print("\nDetalles del error:")
        traceback.print_exc()
    finally:
        metrics.close()
        print("\nConexión cerrada.")


if __name__ == "__main__":
    main()

