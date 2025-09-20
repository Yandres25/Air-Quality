# WAQI Collector: Pipeline de Datos de Calidad del Aire

Este proyecto es un pipeline de datos de streaming diseñado para recolectar, procesar y almacenar información sobre la calidad del aire de la ciudad de Bogotá, Colombia. El flujo de datos utiliza varios servicios de Google Cloud Platform para crear un sistema robusto y escalable.

El pipeline opera de la siguiente manera:

1.  **Recolector de Datos  (main.py en `Cloud Run`)**: Un servicio de Cloud Run se activa mediante un programador (Cloud Scheduler) para ejecutar el script main.py. Este script consulta la API de WAQI, sube los datos a Cloud Storage y notifica a Pub/Sub.
2.  **Mensajería (`Google Pub/Sub`)**: Recibe las notificaciones de los nuevos archivos de datos subidos a Cloud Storage, sirviendo como la fuente de datos para el pipeline de Dataflow.
3.  **Procesamiento (`Google Cloud Dataflow`)**: Un pipeline de streaming que lee los mensajes de Pub/Sub, descarga los archivos de datos desde Cloud Storage, los transforma y los prepara.
4.  **Almacenamiento (`Google BigQuery`)**: El destino final donde se guardan los datos procesados en una tabla estructurada para su posterior análisis y visualización.

---


## Archivos Principales

Este proyecto se basa en los siguientes archivos para su funcionamiento:

* **`main.py`**: El punto de entrada principal del servicio de Cloud Run. Contiene toda la lógica para consultar la API de WAQI, guardar la respuesta como un archivo JSON en un bucket de Google Cloud Storage y enviar una notificación a un tópico de Pub/Sub.

* **`dockerfile`**: Un archivo crucial que le dice a Cloud Build cómo construir la imagen de contenedor de Docker para el servicio de Cloud Run. Define el entorno, copia los archivos de la aplicación (main.py y requirements.txt), instala las dependencias y especifica el comando de inicio.

* **`dataflow_pipeline.py`**: El código de la tubería de Dataflow. Define las transformaciones necesarias para leer los mensajes de Pub/Sub, descargar y procesar los archivos de GCS, y finalmente, insertar los datos limpios en la tabla de BigQuery.

* **`requirements.txt`**: Un archivo que lista todas las bibliotecas de Python que necesita tu script local (`main.py`) para ejecutarse en tu máquina.

* **`requirements_dataflow.txt`**: **Este archivo es crucial**. Contiene solo las dependencias que el pipeline de Dataflow necesita para ejecutarse en la nube. Mantenerlo separado de `requirements.txt` garantiza que el job de Dataflow tenga solo lo necesario.

* **`setup.py`**: Un archivo de configuración que le permite a Dataflow empaquetar y distribuir las dependencias listadas en `requirements_dataflow.txt` y las clases personalizadas (`ReadFromGCS` y `FlattenJsonData`) a sus trabajadores.

* **`README.md`**: Este mismo archivo, que proporciona una descripción del proyecto y sus componentes clave.

---

## Uso del Proyecto

Para ejecutar este pipeline, debes seguir estos pasos:

1.  Asegúrate de tener las credenciales de Google Cloud configuradas correctamente en tu entorno local.
2.  Instala las dependencias de Python para tu entorno de desarrollo:
    ```sh
    pip install -r requirements.txt
    ```
3.  Ejecuta el script de colección de datos para comenzar a poblar GCS y Pub/Sub:
    ```sh
    python main.py
    ```
4.  Ejecuta el pipeline de Dataflow para procesar los datos en streaming. Este comando enviará el trabajo a Google Cloud:
    ```sh
    python dataflow_pipeline.py
    ```


Una vez ejecutado, el trabajo de Dataflow se ejecutará de forma continua en la nube, procesando y almacenando los datos en BigQuery automáticamente.
