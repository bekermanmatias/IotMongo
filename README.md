# Sistema de Almacenamiento Flexible de Datos IoT con MongoDB

Este proyecto implementa un sistema completo de simulación y almacenamiento de datos IoT utilizando MongoDB Atlas como base de datos NoSQL. El sistema genera lecturas simuladas de sensores ambientales (interiores y exteriores) y las almacena en MongoDB para su posterior análisis.

## Estructura del Proyecto

```
IotMongo/
├── sensor_simulator.py      # Generador de lecturas IoT simuladas
├── send_to_mongo.py         # Servicio de envío a MongoDB Atlas
├── queries.py               # Consultas y análisis de datos
├── metrics.py               # Medición de rendimiento del sistema
├── analisis_opcional.py     # Análisis avanzados (promedios por hora, outliers)
├── requirements.txt         # Dependencias del proyecto
├── ejemplos_json.json       # Ejemplos de lecturas JSON generadas
├── diagrama_flujo.txt       # Diagrama ASCII del flujo del sistema
├── seccion_4.2_implementacion.md  # Sección técnica para el paper
└── README.md                # Este archivo
```

## Requisitos Previos

- Python 3.8 o superior
- Cuenta en MongoDB Atlas (gratuita disponible en [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas))
- String de conexión de MongoDB Atlas

## Instalación

1. **Clonar o descargar el repositorio**

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar la conexión a MongoDB Atlas:**
   
   Opción A: Variable de entorno (recomendado)
   ```bash
   # Windows (PowerShell)
   $env:MONGO_URI="mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
   
   # Windows (CMD)
   set MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
   
   # Linux/Mac
   export MONGO_URI="mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"
   ```
   
   Opción B: Editar directamente `send_to_mongo.py`, `queries.py`, `metrics.py` y `analisis_opcional.py` 
   y reemplazar la URI de ejemplo con tu string de conexión real.

## Uso

### 1. Generar Lecturas de Sensores (Prueba del Simulador)

Para probar el simulador y ver ejemplos de lecturas generadas:

```bash
python sensor_simulator.py
```

Este comando mostrará ejemplos de lecturas de sensores interiores y exteriores en formato JSON.

### 2. Enviar Datos a MongoDB Atlas

Para iniciar el envío continuo de lecturas a MongoDB (cada 5 segundos):

```bash
python send_to_mongo.py
```

El script:
- Se conecta a MongoDB Atlas
- Genera lecturas aleatorias cada 5 segundos
- Las inserta en la colección `sensor_readings` de la base de datos `iot_data`
- Muestra cada lectura enviada en consola

**Nota:** Presiona `Ctrl+C` para detener el envío.

### 3. Ejecutar Consultas

Para realizar consultas sobre los datos almacenados:

```bash
python queries.py
```

Este script ejecuta:
- Consulta de los últimos 10 registros
- Cálculo de promedio de temperatura por tipo de sensor
- Filtrado de sensores exteriores
- Conteo de lecturas por dispositivo

### 4. Medir Rendimiento

Para evaluar el rendimiento del sistema (latencia, throughput, tiempo de consultas):

```bash
python metrics.py
```

El script mide:
- Latencia de inserción (mín, máx, promedio, percentiles)
- Tiempo de ejecución de diferentes consultas
- Throughput (inserciones por segundo)

### 5. Análisis Avanzados (Opcional)

Para realizar análisis más complejos:

```bash
python analisis_opcional.py
```

Incluye:
- Promedio de temperatura por hora (últimas 24 horas)
- Conteo detallado de lecturas por sensor
- Detección de valores atípicos usando puntuación Z

## Ejemplos de Lecturas JSON

El archivo `ejemplos_json.json` contiene ejemplos reales de las lecturas generadas por el sistema, mostrando la estructura diferenciada entre sensores interiores y exteriores.

### Sensor Interior:
```json
{
  "device_id": "sensor_01",
  "type": "interior",
  "temperature": 23.7,
  "humidity": 52,
  "light": 340,
  "unit": "C",
  "location": "Sala 1",
  "timestamp": "2025-01-15T14:32:18.123456+00:00"
}
```

### Sensor Exterior:
```json
{
  "device_id": "sensor_02",
  "type": "exterior",
  "temperature": 78.3,
  "light": 850,
  "uv_index": 6.4,
  "unit": "F",
  "location": "Patio",
  "timestamp": "2025-01-15T14:32:18.123456+00:00"
}
```

## Flujo del Sistema

El diagrama completo del flujo se encuentra en `diagrama_flujo.txt`. Resumen:

```
Sensor Simulator → JSON → Python Service → MongoDB Atlas → Queries/Analysis
```

1. **Generación**: El simulador crea lecturas con estructuras variables
2. **Formato**: Los datos se estructuran en JSON
3. **Procesamiento**: El servicio Python valida y prepara los datos
4. **Almacenamiento**: MongoDB Atlas almacena los documentos en formato BSON
5. **Análisis**: Consultas y agregaciones permiten extraer información

## Características Técnicas

- **Esquema flexible**: Soporta documentos con estructuras variables (interior vs exterior)
- **Unidades diferentes**: Maneja temperaturas en Celsius y Fahrenheit simultáneamente
- **Timestamp ISO 8601**: Formato estándar para fechas/horas
- **Conexión segura**: TLS/SSL para comunicación con MongoDB Atlas
- **Manejo de errores**: Gestión robusta de fallos de conexión
- **Métricas de rendimiento**: Evaluación cuantitativa del sistema

## Documentación Académica

El archivo `seccion_4.2_implementacion.md` contiene la sección técnica completa reescrita para el paper académico, incluyendo:

- Descripción detallada del simulador
- Justificación técnica de las decisiones de diseño
- Explicación del flujo completo del sistema
- Descripción de las métricas de rendimiento
- Análisis de las capacidades de MongoDB para IoT

## Solución de Problemas

### Error de conexión a MongoDB
- Verifica que tu string de conexión sea correcto
- Asegúrate de que tu IP esté en la whitelist de MongoDB Atlas
- Verifica que el usuario tenga permisos de escritura

### No se encuentran datos en las consultas
- Ejecuta primero `send_to_mongo.py` para generar datos
- Verifica que la base de datos y colección sean correctas (`iot_data` / `sensor_readings`)

### Dependencias faltantes
```bash
pip install --upgrade pymongo
```

## Autores

- Borda Patricio Alessandro
- Cadabon Dana Natasha
- López Carina
- Rau Bekerman Matías

Universidad Tecnológica Nacional - Facultad Regional La Plata

## Licencia

Este proyecto es parte de un trabajo académico.
