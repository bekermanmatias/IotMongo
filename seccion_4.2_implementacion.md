# 4.2 Implementación

Para evaluar el comportamiento de MongoDB como base de datos para flujos IoT, se implementó un sistema de simulación que genera lecturas sensoriales periódicas y las almacena en MongoDB Atlas. La implementación se estructuró en módulos independientes que permiten la generación, transmisión, almacenamiento y análisis de datos de manera sistemática y reproducible.

## 4.2.1 Simulador de Sensores

El simulador de sensores (`sensor_simulator.py`) constituye el componente inicial del sistema, diseñado para generar lecturas sintéticas que replican el comportamiento de dispositivos IoT reales. Este módulo implementa dos tipos de sensores con características distintas: sensores de tipo *interior* y sensores de tipo *exterior*, cada uno con campos y rangos de valores específicos que reflejan condiciones ambientales realistas.

Los sensores interiores registran temperatura (en grados Celsius), humedad relativa (en porcentaje) y nivel de luminosidad (en lux), mientras que los sensores exteriores capturan temperatura (en grados Fahrenheit), luminosidad y un índice de radiación ultravioleta (UV). Esta diferenciación intencional en la estructura de datos permite validar la capacidad de MongoDB para manejar documentos heterogéneos dentro de una misma colección, sin requerir esquemas rígidos o transformaciones previas.

Cada lectura generada incluye metadatos esenciales como el identificador del dispositivo (`device_id`), el tipo de sensor (`type`), la ubicación física (`location`), la unidad de medida (`unit`) y un timestamp en formato ISO 8601 con zona horaria UTC. El uso de `datetime` y `random` garantiza la variabilidad temporal y de valores necesaria para simular un entorno real, donde las lecturas fluctúan según condiciones ambientales cambiantes.

## 4.2.2 Formato de Datos JSON

Las lecturas generadas se estructuran en formato JSON (JavaScript Object Notation), un estándar ampliamente adoptado en aplicaciones IoT debido a su ligereza, legibilidad y facilidad de procesamiento. MongoDB almacena estos documentos en formato BSON (Binary JSON), una serialización binaria que optimiza el almacenamiento y la eficiencia de consultas, manteniendo la compatibilidad con la estructura JSON original.

A continuación se presentan ejemplos representativos de las lecturas generadas:

**Ejemplo de lectura de sensor interior:**
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

**Ejemplo de lectura de sensor exterior:**
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

La heterogeneidad estructural entre ambos tipos de sensores (presencia de `humidity` solo en interiores, `uv_index` solo en exteriores, y diferentes unidades de temperatura) demuestra la flexibilidad del modelo de documentos de MongoDB para adaptarse a variaciones en el esquema sin requerir migraciones o transformaciones complejas.

## 4.2.3 Integración con MongoDB Atlas

El módulo `send_to_mongo.py` implementa la capa de integración entre el simulador y la base de datos, utilizando el driver oficial `pymongo` para establecer conexión con MongoDB Atlas mediante un string de conexión URI. Este componente actúa como un servicio intermedio que recibe las lecturas generadas, las valida implícitamente y las inserta en la colección `sensor_readings` de la base de datos `iot_data`.

La implementación utiliza el método `insert_one()` de MongoDB para realizar inserciones individuales, registrando cada operación con su timestamp correspondiente. El sistema está configurado para enviar lecturas cada 5 segundos, simulando un flujo continuo de datos típico en entornos IoT. Cada inserción exitosa se registra en consola, mostrando los campos principales de la lectura para facilitar el monitoreo en tiempo real.

La conexión con MongoDB Atlas se establece mediante un mecanismo de autenticación seguro que utiliza TLS/SSL, garantizando la integridad y confidencialidad de los datos durante la transmisión. El sistema implementa manejo de errores para gestionar fallos de conexión, timeouts y errores de inserción, permitiendo la recuperación automática o el registro de incidencias según corresponda.

## 4.2.4 Flujo del Sistema

El flujo completo del sistema puede representarse mediante el siguiente diagrama:

```
┌─────────────────────┐
│  Sensor Simulator   │
│  (sensor_simulator) │
│                     │
│  - Interior sensors │
│  - Exterior sensors │
└──────────┬──────────┘
           │
           │ Genera lecturas JSON
           │ cada 5 segundos
           ▼
┌─────────────────────┐
│  Python Service     │
│  (send_to_mongo.py) │
│                     │
│  - Validación       │
│  - Formato JSON     │
│  - Conexión MongoDB │
└──────────┬──────────┘
           │
           │ Inserta documentos
           │ vía pymongo
           ▼
┌─────────────────────┐
│  MongoDB Atlas      │
│                     │
│  - Colección:       │
│    sensor_readings  │
│  - Base: iot_data   │
└──────────┬──────────┘
           │
           │ Consultas y agregaciones
           ▼
┌─────────────────────┐
│  Analysis Layer     │
│  (queries.py)       │
│                     │
│  - Últimos registros│
│  - Promedios        │
│  - Filtros          │
│  - Agregaciones     │
└─────────────────────┘
```

Este flujo unidireccional desde la generación hasta el almacenamiento y análisis permite validar cada etapa del proceso, desde la creación de datos heterogéneos hasta su persistencia y consulta eficiente.

## 4.2.5 Consultas y Análisis

El módulo `queries.py` implementa un conjunto de consultas representativas que demuestran las capacidades de MongoDB para el análisis de datos IoT. Estas consultas incluyen:

1. **Consulta de registros recientes**: Obtiene los últimos N registros ordenados por timestamp, utilizando índices para optimizar el rendimiento de ordenamiento temporal.

2. **Agregación de promedios por tipo**: Utiliza el framework de agregación de MongoDB para calcular promedios, mínimos y máximos de temperatura agrupados por tipo de sensor. Esta consulta incluye una transformación que normaliza las temperaturas a grados Celsius para permitir comparaciones consistentes entre sensores con diferentes unidades.

3. **Filtrado por tipo de sensor**: Demuestra la capacidad de MongoDB para realizar consultas selectivas sobre documentos con estructuras variables, filtrando específicamente sensores exteriores mediante el campo `type`.

4. **Conteo de lecturas por dispositivo**: Utiliza operaciones de agregación para contar el número de lecturas generadas por cada sensor, facilitando el análisis de distribución de datos y detección de dispositivos con mayor actividad.

Estas consultas validan la eficiencia de MongoDB para manejar tanto operaciones simples de lectura como agregaciones complejas sobre grandes volúmenes de datos, características esenciales para sistemas IoT que requieren análisis en tiempo real.

## 4.2.6 Métricas de Rendimiento

El módulo `metrics.py` implementa un sistema de medición de rendimiento que evalúa aspectos críticos del sistema:

1. **Latencia de inserción**: Mide el tiempo transcurrido entre la generación de una lectura y su confirmación de inserción en MongoDB. Esta métrica se calcula sobre múltiples inserciones (por defecto 100) para obtener estadísticas robustas, incluyendo latencia mínima, máxima, promedio, mediana, desviación estándar y percentiles 95 y 99. Estas métricas permiten identificar la consistencia y predictibilidad del rendimiento de escritura.

2. **Tiempo de ejecución de consultas**: Evalúa el rendimiento de diferentes tipos de consultas, desde búsquedas simples con filtros hasta agregaciones complejas. Esta medición permite comparar la eficiencia relativa de diferentes operaciones y optimizar aquellas que presenten cuellos de botella.

3. **Throughput**: Calcula el número de inserciones que el sistema puede procesar por segundo durante un período determinado. Esta métrica es fundamental para determinar la capacidad del sistema para manejar flujos de datos de alta frecuencia, típicos en entornos IoT con múltiples dispositivos concurrentes.

Las métricas se presentan en formato tabular con unidades claras (milisegundos para latencia, inserciones por segundo para throughput), facilitando la interpretación y comparación con otros sistemas o configuraciones.

## 4.2.7 Justificación Técnica

La elección de MongoDB como sistema de almacenamiento para este caso de uso se fundamenta en varias características técnicas que lo hacen especialmente adecuado para entornos IoT:

- **Flexibilidad de esquema**: La capacidad de almacenar documentos con estructuras variables permite incorporar nuevos tipos de sensores o modificar campos existentes sin requerir migraciones de esquema, reduciendo el tiempo de desarrollo y mantenimiento.

- **Escalabilidad horizontal**: MongoDB Atlas permite escalar automáticamente según la demanda, esencial para sistemas IoT que pueden experimentar picos de carga impredecibles.

- **Rendimiento de escritura**: El modelo orientado a documentos y la optimización de BSON permiten inserciones rápidas, críticas para sistemas que procesan flujos continuos de datos.

- **Capacidades de agregación**: El framework de agregación de MongoDB permite realizar análisis complejos directamente en la base de datos, reduciendo la necesidad de procesamiento externo y mejorando la eficiencia general del sistema.

- **Integración con ecosistemas modernos**: La compatibilidad nativa con JSON facilita la integración con APIs REST, servicios web y herramientas de análisis, componentes comunes en arquitecturas IoT modernas.

Esta implementación demuestra empíricamente cómo MongoDB puede gestionar eficientemente datos heterogéneos y variables provenientes de dispositivos IoT, validando su idoneidad como solución de almacenamiento flexible para este tipo de aplicaciones.

