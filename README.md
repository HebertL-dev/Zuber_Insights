# Zuber - Análisis de Datos de Viajes Compartidos en Chicago

## Descripción del Proyecto

Este proyecto está orientado a analizar patrones en los viajes realizados por Zuber, una nueva empresa de viajes compartidos que se está lanzando en Chicago. El objetivo es encontrar patrones en los viajes de taxi, analizar las preferencias de los pasajeros y explorar el impacto del clima en la frecuencia de los viajes.

El análisis incluye:
1. **Estudio de la base de datos de viajes**: Analizando los datos de los taxis, los barrios, las condiciones meteorológicas y las rutas de los viajes.
2. **Prueba de hipótesis**: Evaluación del impacto del clima (en particular, los días lluviosos) en la duración de los viajes.
3. **Análisis de patrones**: Descubrimiento de tendencias y patrones en los viajes de taxi, identificando correlaciones entre los factores climáticos y la duración de los viajes.

## Estructura del Proyecto

- **neighborhoods**: Datos sobre los barrios de la ciudad de Chicago.
  - `name`: Nombre del barrio
  - `neighborhood_id`: Código del barrio
- **cabs**: Datos sobre los taxis de Zuber.
  - `cab_id`: Código del vehículo
  - `vehicle_id`: ID técnico del vehículo
  - `company_name`: Empresa propietaria del vehículo
- **trips**: Datos sobre los viajes realizados.
  - `trip_id`: Código del viaje
  - `cab_id`: Código del vehículo que opera el viaje
  - `start_ts`: Fecha y hora de inicio del viaje (redondeada a la hora)
  - `end_ts`: Fecha y hora de finalización del viaje (redondeada a la hora)
  - `duration_seconds`: Duración del viaje en segundos
  - `distance_miles`: Distancia del viaje en millas
  - `pickup_location_id`: Código del barrio de recogida
  - `dropoff_location_id`: Código del barrio de finalización
- **weather_records**: Datos sobre el clima en Chicago.
  - `record_id`: Código del registro meteorológico
  - `ts`: Fecha y hora del registro (redondeada a la hora)
  - `temperature`: Temperatura cuando se tomó el registro
  - `description`: Descripción de las condiciones meteorológicas (ej. "lluvia ligera", "nubes dispersas")

## Objetivo del Proyecto

El objetivo es analizar cómo las condiciones meteorológicas, en particular los días lluviosos, afectan la duración de los viajes en taxi. Se probará una hipótesis sobre si los días lluviosos tienen un tiempo de viaje diferente en comparación con los días sin lluvia.

## Metodología

1. **Preprocesamiento de Datos**: Limpieza de datos y preparación para el análisis.
2. **Análisis de Correlación**: Identificación de las variables relevantes y su relación con el tiempo de viaje.
3. **Prueba de Hipótesis**: Realización de una prueba t para comparar la duración de los viajes en días lluviosos y no lluviosos.

## Consulta SQL

Para obtener los datos necesarios, se realizó una consulta SQL que selecciona los viajes realizados en los días sábados en los cuales el clima es lluvioso o no, y se asocia con las condiciones meteorológicas. La consulta se ejecuta sobre las tablas `trips` y `weather_records`:

SELECT 
    t.start_ts, 
    CASE 
        WHEN LOWER(w.description) LIKE '%rain%' OR LOWER(w.description) LIKE '%storm%' THEN 'Bad'
        ELSE 'Good'
    END AS weather_conditions,
    t.duration_seconds
FROM 
    trips t
JOIN 
    weather_records w ON DATE_TRUNC('hour', t.start_ts) = DATE_TRUNC('hour', w.ts)
WHERE 
    t.pickup_location_id = 50  -- Loop
    AND t.dropoff_location_id = 63  -- O'Hare
    AND EXTRACT(DOW FROM t.start_ts) = 6  -- Saturday (DOW: 6 represents Saturday)
ORDER BY 
    t.trip_id;

## Conclusión

Se formuló una **hipótesis nula (H₀)** bajo la suposición de que **no hay diferencia en el tiempo promedio de viaje entre los días lluviosos y no lluviosos**. Por otro lado, la **hipótesis alternativa (H₁)** sugiere que **sí existe una diferencia en el tiempo promedio de viaje** entre ambos tipos de días.

Dado que los datos provienen de **dos conjuntos independientes**, se utilizó la **prueba t de Student (t-test)** para evaluar la diferencia entre los tiempos promedio de viaje. Se estableció un nivel de significancia de **0.05**, lo que significa que si el **valor p** es menor a 0.05, se rechazaría la hipótesis nula (H₀).

Los resultados obtenidos fueron los siguientes:
- **T-statistic**: 6.946
- **P-value**: 6.52 × 10⁻¹²

Dado que el valor p es **mucho menor** a 0.05, **rechazamos la hipótesis nula (H₀)** y concluimos que existe una diferencia significativa en el tiempo promedio de viaje entre los días lluviosos y los no lluviosos. Esto sugiere que **los días lluviosos tienen un tiempo de viaje diferente**, posiblemente más largo, en comparación con los días sin lluvia.

## Archivos del Proyecto

- **notebook.ipynb**: Cuaderno Jupyter que contiene el análisis de los datos.
- **moved_project_sql_result_01.csv**: Resultado de la consulta SQL (Archivo 01).
- **moved_project_sql_result_04.csv**: Resultado de la consulta SQL (Archivo 04).
- **moved_project_sql_result_07.csv**: Resultado de la consulta SQL (Archivo 07).

## Cómo Ejecutar el Proyecto

1. Clona este repositorio en tu máquina local.
2. Abre el archivo `notebook.ipynb` en Jupyter Notebook o JupyterLab.
3. Ejecuta las celdas para realizar el análisis.

## Requisitos

- Python 3.x
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SciPy

Instala las dependencias con:

```bash
pip install pandas numpy matplotlib seaborn scipy
