"""
Simulador de sensores IoT para generación de lecturas ambientales.
Genera datos simulados para sensores de tipo interior y exterior con estructuras distintas.
"""

import random
import json
from datetime import datetime, timezone
from typing import Dict, Any


class SensorSimulator:
    """Clase para simular lecturas de sensores IoT."""
    
    def __init__(self):
        """Inicializa el simulador con rangos de valores realistas."""
        # Rangos para sensores interiores
        self.interior_temp_range = (18.0, 28.0)  # °C
        self.interior_humidity_range = (30, 70)  # %
        self.interior_light_range = (100, 500)  # lux
        
        # Rangos para sensores exteriores
        self.exterior_temp_range = (5.0, 35.0)  # °C (convertido a °F en el sensor)
        self.exterior_light_range = (200, 1000)  # lux
        self.uv_index_range = (0.0, 11.0)
        
        # IDs de sensores disponibles
        self.interior_sensors = ["sensor_01", "sensor_03", "sensor_05"]
        self.exterior_sensors = ["sensor_02", "sensor_04", "sensor_06"]
        
        # Ubicaciones predefinidas
        self.interior_locations = ["Sala 1", "Sala 2", "Oficina A", "Oficina B"]
        self.exterior_locations = ["Patio", "Jardín", "Terraza", "Entrada"]
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convierte temperatura de Celsius a Fahrenheit."""
        return round((celsius * 9/5) + 32, 1)
    
    def generate_interior_reading(self, device_id: str = None) -> Dict[str, Any]:
        """
        Genera una lectura simulada de un sensor interior.
        
        Args:
            device_id: ID del dispositivo. Si es None, se selecciona aleatoriamente.
        
        Returns:
            Dict con la lectura del sensor en formato JSON.
        """
        if device_id is None:
            device_id = random.choice(self.interior_sensors)
        
        temperature = round(random.uniform(*self.interior_temp_range), 1)
        humidity = random.randint(*self.interior_humidity_range)
        light = random.randint(*self.interior_light_range)
        location = random.choice(self.interior_locations)
        
        reading = {
            "device_id": device_id,
            "type": "interior",
            "temperature": temperature,
            "humidity": humidity,
            "light": light,
            "unit": "C",
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return reading
    
    def generate_exterior_reading(self, device_id: str = None) -> Dict[str, Any]:
        """
        Genera una lectura simulada de un sensor exterior.
        
        Args:
            device_id: ID del dispositivo. Si es None, se selecciona aleatoriamente.
        
        Returns:
            Dict con la lectura del sensor en formato JSON.
        """
        if device_id is None:
            device_id = random.choice(self.exterior_sensors)
        
        temp_celsius = random.uniform(*self.exterior_temp_range)
        temperature = self._celsius_to_fahrenheit(temp_celsius)
        light = random.randint(*self.exterior_light_range)
        uv_index = round(random.uniform(*self.uv_index_range), 1)
        location = random.choice(self.exterior_locations)
        
        reading = {
            "device_id": device_id,
            "type": "exterior",
            "temperature": temperature,
            "light": light,
            "uv_index": uv_index,
            "unit": "F",
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return reading
    
    def generate_random_reading(self) -> Dict[str, Any]:
        """
        Genera una lectura aleatoria de cualquier tipo de sensor.
        
        Returns:
            Dict con la lectura del sensor en formato JSON.
        """
        sensor_type = random.choice(["interior", "exterior"])
        
        if sensor_type == "interior":
            return self.generate_interior_reading()
        else:
            return self.generate_exterior_reading()
    
    def reading_to_json(self, reading: Dict[str, Any]) -> str:
        """
        Convierte una lectura a formato JSON string.
        
        Args:
            reading: Dict con la lectura del sensor.
        
        Returns:
            String JSON formateado.
        """
        return json.dumps(reading, indent=2, ensure_ascii=False)


def main():
    """Función principal para probar el simulador."""
    simulator = SensorSimulator()
    
    print("=== Simulador de Sensores IoT ===\n")
    
    # Generar y mostrar lecturas de ejemplo
    print("Lectura de sensor interior:")
    interior_reading = simulator.generate_interior_reading()
    print(simulator.reading_to_json(interior_reading))
    print()
    
    print("Lectura de sensor exterior:")
    exterior_reading = simulator.generate_exterior_reading()
    print(simulator.reading_to_json(exterior_reading))
    print()
    
    print("Lectura aleatoria:")
    random_reading = simulator.generate_random_reading()
    print(simulator.reading_to_json(random_reading))


if __name__ == "__main__":
    main()

