"""
Script para medir el tiempo que demora en subir datos a MongoDB Atlas.
Muestra el tiempo de cada inserción individual y estadísticas generales.
"""

import os
import time
from pymongo import MongoClient
from sensor_simulator import SensorSimulator
from datetime import datetime

# Obtener URI de MongoDB
mongo_uri = os.getenv(
    "MONGO_URI",
    "mongodb+srv://natashacadabon:Natasha1234@iotcluster.55iunlr.mongodb.net/?appName=IoTCluster"
)

def medir_tiempo_subida(num_documentos=10):
    """
    Mide el tiempo que demora en subir documentos a MongoDB.
    
    Args:
        num_documentos: Número de documentos a insertar para la prueba
    """
    print("="*80)
    print("MEDICION DE TIEMPO DE SUBIDA A MONGODB ATLAS")
    print("="*80)
    
    simulator = SensorSimulator()
    
    try:
        print("\n[1] Conectando a MongoDB Atlas...")
        start_connect = time.perf_counter()
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        db = client["iot_data"]
        collection = db["sensor_readings"]
        end_connect = time.perf_counter()
        tiempo_conexion = (end_connect - start_connect) * 1000
        print(f"    [OK] Conexion establecida en {tiempo_conexion:.2f} ms")
        
        print(f"\n[2] Insertando {num_documentos} documentos...")
        print("-" * 80)
        
        tiempos_insercion = []
        tiempos_totales = []
        
        for i in range(num_documentos):
            # Generar lectura
            lectura = simulator.generate_random_reading()
            
            # Medir tiempo TOTAL (generacion + insercion)
            inicio_total = time.perf_counter()
            
            # Medir solo tiempo de INSERCION
            inicio_insercion = time.perf_counter()
            try:
                result = collection.insert_one(lectura)
                fin_insercion = time.perf_counter()
                fin_total = time.perf_counter()
                
                if result.inserted_id:
                    tiempo_insercion_ms = (fin_insercion - inicio_insercion) * 1000
                    tiempo_total_ms = (fin_total - inicio_total) * 1000
                    
                    tiempos_insercion.append(tiempo_insercion_ms)
                    tiempos_totales.append(tiempo_total_ms)
                    
                    # Mostrar cada inserción
                    print(f"  Documento #{i+1:2d}: {tiempo_insercion_ms:6.2f} ms "
                          f"(total: {tiempo_total_ms:6.2f} ms) - "
                          f"{lectura['device_id']} ({lectura['type']})")
                else:
                    print(f"  Documento #{i+1:2d}: [ERROR] No se inserto")
            except Exception as e:
                print(f"  Documento #{i+1:2d}: [ERROR] {e}")
        
        # Estadísticas
        if tiempos_insercion:
            print("\n" + "="*80)
            print("ESTADISTICAS DE TIEMPO DE SUBIDA")
            print("="*80)
            
            print("\n[Tiempo de INSERCION en MongoDB]")
            print(f"  Minimo:     {min(tiempos_insercion):.2f} ms")
            print(f"  Maximo:     {max(tiempos_insercion):.2f} ms")
            print(f"  Promedio:   {sum(tiempos_insercion)/len(tiempos_insercion):.2f} ms")
            print(f"  Total:      {sum(tiempos_insercion):.2f} ms")
            
            print("\n[Tiempo TOTAL (generacion + insercion)]")
            print(f"  Minimo:     {min(tiempos_totales):.2f} ms")
            print(f"  Maximo:     {max(tiempos_totales):.2f} ms")
            print(f"  Promedio:   {sum(tiempos_totales)/len(tiempos_totales):.2f} ms")
            print(f"  Total:      {sum(tiempos_totales):.2f} ms")
            
            # Calcular throughput
            tiempo_total_segundos = sum(tiempos_insercion) / 1000
            throughput = len(tiempos_insercion) / tiempo_total_segundos if tiempo_total_segundos > 0 else 0
            
            print("\n[Throughput]")
            print(f"  Documentos insertados: {len(tiempos_insercion)}")
            print(f"  Tiempo total: {tiempo_total_segundos:.2f} segundos")
            print(f"  Velocidad: {throughput:.2f} documentos/segundo")
            
            # Comparación
            print("\n[Comparacion]")
            tiempo_promedio_seg = (sum(tiempos_insercion)/len(tiempos_insercion)) / 1000
            print(f"  Cada documento tarda en promedio: {tiempo_promedio_seg*1000:.2f} ms")
            print(f"  En 1 segundo puedes subir aproximadamente: {1/tiempo_promedio_seg:.0f} documentos")
            
        print("\n" + "="*80)
        
        client.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


def medir_tiempo_lote(num_documentos=100):
    """
    Mide el tiempo de subir múltiples documentos en un lote.
    """
    print("\n" + "="*80)
    print("MEDICION DE TIEMPO DE SUBIDA EN LOTE")
    print("="*80)
    
    simulator = SensorSimulator()
    
    try:
        print("\n[1] Conectando a MongoDB Atlas...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        db = client["iot_data"]
        collection = db["sensor_readings"]
        print("    [OK] Conexion establecida")
        
        print(f"\n[2] Generando {num_documentos} documentos...")
        documentos = [simulator.generate_random_reading() for _ in range(num_documentos)]
        print("    [OK] Documentos generados")
        
        print(f"\n[3] Insertando {num_documentos} documentos en MongoDB...")
        inicio = time.perf_counter()
        
        # Insertar uno por uno (como lo hace el sistema real)
        insertados = 0
        for doc in documentos:
            try:
                collection.insert_one(doc)
                insertados += 1
            except Exception as e:
                print(f"    [ERROR] Error al insertar: {e}")
        
        fin = time.perf_counter()
        
        tiempo_total = fin - inicio
        tiempo_promedio = (tiempo_total / insertados) * 1000 if insertados > 0 else 0
        throughput = insertados / tiempo_total if tiempo_total > 0 else 0
        
        print("\n" + "="*80)
        print("RESULTADOS DE SUBIDA EN LOTE")
        print("="*80)
        print(f"\n  Documentos insertados: {insertados}/{num_documentos}")
        print(f"  Tiempo total: {tiempo_total:.2f} segundos")
        print(f"  Tiempo promedio por documento: {tiempo_promedio:.2f} ms")
        print(f"  Throughput: {throughput:.2f} documentos/segundo")
        print(f"\n  Para subir 1000 documentos: ~{1000/throughput:.1f} segundos" if throughput > 0 else "")
        print(f"  Para subir 10000 documentos: ~{10000/throughput:.1f} segundos" if throughput > 0 else "")
        
        print("\n" + "="*80)
        
        client.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    print("\nEste script mide el tiempo que demora en subir datos a MongoDB Atlas.\n")
    
    # Modo 1: Medición detallada de pocos documentos
    print("="*80)
    print("MODO 1: Medicion detallada (10 documentos)")
    print("="*80)
    medir_tiempo_subida(num_documentos=10)
    
    # Hacer prueba en lote automáticamente
    print("\n" + "="*80)
    print("MODO 2: Prueba en lote (100 documentos)")
    print("="*80)
    medir_tiempo_lote(num_documentos=100)

