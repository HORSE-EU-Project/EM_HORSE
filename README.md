

# 🛡️ Threat Modeling API

This **FastAPI**-based service acts as a centralized API and data converter for threat modeling. It bridges the gap between high-level attack definitions (in **JSON**) and specialized security services that require **XML** formatting, such as Digital Twins and network policy managers.

## 🚀 Key Endpoints

### 1. Modeling & Orchestration

| Endpoint | Method | Description |
| --- | --- | --- |
| `/modeling` | `POST` | **Global Orchestrator**. Simultaneously triggers both Digital Twins workflows. |
| `/modeling_DTs` | `POST` | Converts JSON to XML, saves it as a local file, and forwards it to the **Digital Twin** service (`DT_URL`). |
| `/modeling_DDoS` | `POST` | Converts JSON to XML and sends it as an asynchronous stream to the **UMU IA-NDT** service (`UMU_URL`). |

### 2. Network Analysis

* **`GET /search-pcap`**: Queries the **Elasticsearch** instance (`SM_URL`) to retrieve network traffic logs from the **last 2 minutes**. Perfect for real-time threat detection validation.

### 3. Utilities

* **`GET /hello`**: Basic health check to confirm the API is responsive.
* **`POST /upload`**: A debug/echo endpoint that returns the raw request body as plain text.


## 🛠️ Configuration & Services

The API interacts with several external services defined in the environment:

* **Elasticsearch (SM):** `http://10.19.2.15:9200` (Used for PCAP data retrieval).
* **Digital Twin (DT):** `http://10.208.11.75:5000` (Receives XML files via multipart upload).
* **UMU Service:** `http://10.208.11.74:5005` (Receives raw XML policies).

### Prerequisites

* Python 3.8+
* Dependencies: `fastapi`, `uvicorn`, `requests`, `httpx`

### Installation & Run

```bash
# Install dependencies
pip install fastapi uvicorn requests httpx

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000

```
