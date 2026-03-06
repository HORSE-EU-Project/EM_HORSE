# 🛡️ Threat Modeling & Network API

Esta API, construida con **FastAPI**, actúa como un orquestador y convertidor de datos para el modelado de amenazas. Su función principal es recibir definiciones de ataques en formato **JSON**, transformarlas a **XML** y distribuirlas a diferentes servicios de seguridad (Digital Twins, UMU, etc.).

## 🚀 Endpoints Principales

### Modelado de Amenazas (Orquestación)

| Endpoint | Método | Descripción |
| --- | --- | --- |
| `/modeling` | `POST` | **Orquestador global**. Llama internamente a los endpoints de DTs y DDoS simultáneamente. |
| `/modeling_DTs` | `POST` | Convierte el JSON a un archivo XML y lo envía al servicio de **Digital Twin** (`DT_URL`). |
| `/modeling_DDoS` | `POST` | Convierte el JSON a XML y lo envía como cuerpo de mensaje al servicio **UMU** (`UMU_URL`). |

### Análisis de Tráfico

* **`GET /search-pcap`**: Realiza una consulta a **Elasticsearch** para obtener los logs de tráfico de red (`pcap_data`) de los últimos **2 minutos**. Requiere que el servicio de ELK esté operativo.

### Conversión Específica (JSON to XML)

Estos endpoints procesan la estructura de datos pero retornan la respuesta directamente al cliente:

* **`POST /dnsAmplificationAttack`**: Especializado en modelos de ataque por amplificación DNS.
* **`POST /ntpattack`**: Especializado en modelos de ataque basados en protocolo NTP.

### Utilidades

* **`GET /hello`**: Health check básico para verificar que la API está online.
* **`POST /upload`**: Endpoint de prueba que devuelve el cuerpo de la petición en texto plano.

---

## 🛠️ Lógica de Conversión (JSON ↔ XML)

La API incluye una función personalizada `json_to_xml` que soporta atributos.

> [!TIP]
> **Regla de Atributos:** Si una clave en el JSON comienza con `_` o `-` (ej. `"_id": "123"`), se convertirá automáticamente en un **atributo** del nodo XML en lugar de un sub-elemento.

---

## 🔧 Configuración y Variables

La API se comunica con los siguientes servicios externos (configurables en el código):

* **Elasticsearch:** `http://10.19.2.15:9200`
* **Digital Twin Service:** `http://10.208.11.75:5000`
* **UMU Service:** `http://10.208.11.74:5005`

### Requisitos

```bash
pip install fastapi uvicorn requests httpx

```

### Ejecución

```bash
uvicorn main:app --reload

```
