# Cómo Medir el Tiempo de Subida a MongoDB

Existen **3 formas** de medir cuánto tiempo demora en subir datos a MongoDB Atlas:

## Método 1: Script Simple y Detallado (`medir_tiempo_subida.py`)

**El más fácil de entender y usar.**

```bash
python medir_tiempo_subida.py
```

**Qué muestra:**
- Tiempo de cada inserción individual
- Tiempo promedio, mínimo y máximo
- Throughput (documentos por segundo)
- Comparaciones útiles

**Ejemplo de salida:**
```
Tiempo de INSERCION en MongoDB:
  Minimo:     49.50 ms
  Maximo:     69.20 ms
  Promedio:   56.09 ms
  
Throughput: 17.83 documentos/segundo
```

---

## Método 2: Script de Métricas Completo (`metrics.py`)

**El más completo y profesional.**

```bash
python metrics.py
```

**Qué muestra:**
- Latencia de inserción con estadísticas avanzadas (percentiles p95, p99)
- Tiempo de ejecución de consultas
- Throughput en tiempo real
- 100 inserciones de prueba

**Ejemplo de salida:**
```
[1] LATENCIA DE INSERCIÓN
  Latencia promedio: 57.45 ms
  Latencia mediana: 56.29 ms
  Percentil 95: 71.58 ms
  Percentil 99: 74.51 ms

[3] THROUGHPUT
  Throughput: 17.14 inserciones/segundo
```

---

## Método 3: Medición Manual en tu Código

Si quieres medir el tiempo en tu propio código:

```python
import time
from pymongo import MongoClient

# Conectar
client = MongoClient("tu_uri_mongodb")
collection = client["iot_data"]["sensor_readings"]

# Medir tiempo de inserción
inicio = time.perf_counter()
result = collection.insert_one(tu_documento)
fin = time.perf_counter()

tiempo_ms = (fin - inicio) * 1000
print(f"Tiempo de inserción: {tiempo_ms:.2f} ms")
```

---

## ¿Cuál Usar?

- **Para pruebas rápidas y entender el concepto**: `medir_tiempo_subida.py`
- **Para métricas profesionales y el paper**: `metrics.py`
- **Para integrar en tu código**: Método 3

---

## Interpretación de Resultados

### Tiempo de Inserción Típico
- **Excelente**: < 50 ms
- **Bueno**: 50-100 ms
- **Aceptable**: 100-200 ms
- **Lento**: > 200 ms

### Throughput Típico
- **Excelente**: > 20 documentos/segundo
- **Bueno**: 10-20 documentos/segundo
- **Aceptable**: 5-10 documentos/segundo

### Factores que Afectan el Tiempo
1. **Latencia de red**: Distancia al servidor de MongoDB Atlas
2. **Tamaño del documento**: Documentos más grandes tardan más
3. **Carga del servidor**: MongoDB Atlas puede estar ocupado
4. **Índices**: Más índices pueden hacer las inserciones más lentas

---

## Ejemplo Real de tus Resultados

Basado en tus pruebas anteriores:
- **Tiempo promedio**: ~57 ms por documento
- **Throughput**: ~17 documentos/segundo
- **Para 1000 documentos**: ~58 segundos
- **Para 10000 documentos**: ~9.7 minutos

**Conclusión**: Tu sistema tiene un rendimiento **BUENO** para aplicaciones IoT.

