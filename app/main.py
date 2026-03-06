
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPBasicAuth
import httpx

app = FastAPI()

# URLs de servicios externos
SM_URL = "http://10.19.2.15:9200/pcap_data/_search"  # URL del servicio Elasticsearch
P_URL = "http://localhost:8000/upload"              # URL del servicio de carga
DT_URL =  "http://10.208.11.75:5000/upload"
UMU_URL = "http://10.208.11.74:5005/from_em"  # URL del servicio UMU

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

#DT Fabrizio only
@app.post("/modeling_DTs", response_class=Response)
async def modeling_handler(request: Request):
    print("Received request for modeling")
    """
    Maneja el modelado de amenazas convirtiendo JSON a XML y enviándolo a un servicio externo.
    
    PRE: 
    - El request debe contener un JSON válido en el cuerpo
    - El JSON debe ser convertible a XML usando la función json_to_xml
    - El servicio en DT_URL debe estar disponible y funcional
    
    POST:
    - Retorna una Response con contenido XML si la operación es exitosa
    - Retorna error 500 si hay problemas en la comunicación o conversión
    - El media_type de la respuesta es "application/xml"
    
    Funcionalidad:
    Esta función actúa como un proxy que recibe datos JSON, los convierte a XML
    y los reenvía a un servicio externo para su procesamiento.
    """
    # Extraer datos JSON del request
    data = await request.json()
    print(f"Receiving incoming JSON attack model for DNS_Amplification (attacker: {data.get('attacker')}, victim: {data.get('victim')}, duration: {data.get('duration')})")

    
    # Convertir JSON a formato XML
    print("Converting JSON to XML...")
    xml_str = json_to_xml(data)
    print("Conversion complete:")
    xml_tree = ET.ElementTree(ET.fromstring(xml_str))
    ET.indent(xml_tree, space="  ", level=0)
    xml_tree.write("converted.xml", encoding="utf-8", xml_declaration=True)
    with open("converted.xml", "r", encoding="utf-8") as f:
        print(f.read())

    # Preparar y enviar XML como archivo multipart/form-data
    print("Sending XML file to PP-NDT on " + DT_URL + "...")
    try:
        # Enviamos el archivo generado 'converted.xml' como campo 'file'
        with open("converted.xml", "rb") as f:
            files = {
                "file": f
            }
            post_response = requests.post(DT_URL, files=files)
        print("XML file sent successfully, received response:")
        # Retornar respuesta del servicio externo
        return Response(content=post_response.text, media_type="application/xml")
    except Exception as e:
        print(f"Error al enviar el XML como archivo: {e}")
        return Response(content="Error en el envío", status_code=500)


    # Nota: el bloque siguiente (envío a P_URL) se conserva en caso de necesitarlo en el futuro
    # (se mantiene como alternativa para enviar el XML directamente en el body)
    # Extraer datos JSON del request
    data = await request.json()
    
    # Convertir JSON a formato XML
    xml_str = json_to_xml(data)
    
    try:
        # Preparar headers para envío de XML
        headers = {'Content-Type': 'application/xml'}
        
        # Enviar XML al servicio externo
        post_response = requests.post(P_URL, data=xml_str.encode("utf-8"), headers=headers)
        post_response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        # Retornar respuesta del servicio externo
        return Response(content=post_response.text, media_type="application/xml")
    except Exception as e:
        print(f"Error al enviar el XML: {e}")
        return Response(content="Error en el envío", status_code=500)


#DT Fabritcio and UMU
@app.post("/modeling", response_class=Response)
async def modeling_handler(request: Request):
    # Llamar a /modeling_DTs
    print("Calling /modeling_DTs...")
    try:
        # Reenviar el request a /modeling_DTs
        body = await request.body()
        async with httpx.AsyncClient(timeout=30.0) as client:
            dt_response = await client.post("http://localhost:8000/modeling_DTs", content=body, headers={"Content-Type": "application/json"})
            dt_response.raise_for_status()
        print("Response from /modeling_DTs received successfully")
    except Exception as e:
        return Response(content=f"Error al llamar /modeling_DTs: {e}", status_code=500)
    
    # Llamar a /modeling_DDoS
    print("Calling /modeling_DDoS...")
    try:
        # Reenviar el request a /modeling_DDoS
        body = await request.body()
        async with httpx.AsyncClient(timeout=30.0) as client:
            ddos_response = await client.post("http://localhost:8000/modeling_DDoS", content=body, headers={"Content-Type": "application/json"})
            ddos_response.raise_for_status()
        print("Response from /modeling_DDoS received successfully")
    except Exception as e:
        return Response(content=f"Error al llamar /modeling_DDoS: {e}", status_code=500)
    
    return Response(content="Both modeling endpoints called successfully", media_type="application/json")

#UMU only
@app.post("/modeling_DDoS", response_class=Response)
async def modeling_handler(request: Request):
    try:
        # Extraer JSON del request
        data = await request.json()
        print(f"Receiving incoming JSON attack model for DNS_Amplification (attacker: {data.get('attacker')}, victim: {data.get('victim')}, duration: {data.get('duration')})")
    except Exception as e:
        return Response(content=f"Error leyendo JSON: {e}", status_code=400)

    # Convertir JSON a XML
    try:
        print("Converting JSON to XML...")
        xml_str = json_to_xml(data)
        print("Conversion complete:")
        #printa del xml con la estructura bien identada
        xml_tree = ET.ElementTree(ET.fromstring(xml_str))
        ET.indent(xml_tree, space="  ", level=0)
        xml_tree.write("converted.xml", encoding="utf-8", xml_declaration=True)
        with open("converted.xml", "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        return Response(content=f"Error convirtiendo JSON a XML: {e}", status_code=500)

    headers = {'Content-Type': 'application/xml'}

    try:
        # Enviar XML de manera asíncrona con httpx
        print("Sending XML policy to IA-NDT on"+ UMU_URL+"...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            post_response = await client.post(UMU_URL, content=xml_str.encode("utf-8"), headers=headers)
            post_response.raise_for_status()
        print("XML sent successfully to IA-NDT, received response:")
        return Response(content=post_response.text, media_type="application/xml")
    except httpx.HTTPStatusError as e:
        return Response(content=f"Error HTTP al enviar XML: {e.response.status_code}", status_code=502)
    except Exception as e:
        return Response(content=f"Error al enviar XML: {e}", status_code=500)



# Endpoint de upload
@app.post("/upload")
async def upload(request: Request):
    try:
        body = await request.body()
        return PlainTextResponse(content=body.decode("utf-8"))
    except Exception as e:
        return PlainTextResponse(content=f"Error leyendo body: {e}", status_code=400)


@app.get("/search-pcap")
def search_pcap():
    """
    Busca datos de PCAP en Elasticsearch dentro de un rango de tiempo específico.
    
    PRE:
    - El servicio Elasticsearch debe estar disponible en SM_URL
    - Las credenciales de autenticación deben ser válidas ('elastic', 'HoR$e2024!eLk@sPh#ynX')
    - El índice 'pcap_data' debe existir en Elasticsearch
    - Los documentos deben tener el campo 'frame.frame_frame_time_utc'
    
    POST:
    - Retorna un objeto JSON con los resultados de la búsqueda si es exitosa
    - Lanza HTTPException con status_code 500 si hay errores
    - Los datos incluyen hits de Elasticsearch de los últimos 2 minutos
    
    Funcionalidad:
    Realiza una consulta a Elasticsearch para obtener datos de tráfico de red
    capturados en los últimos 2 minutos. Utiliza autenticación básica y
    filtra por timestamp UTC.
    """
    try:
        # Configurar headers para la petición JSON
        headers = {"Content-Type": "application/json"}
        
        # Configurar autenticación básica para Elasticsearch
        auth = HTTPBasicAuth('elastic', 'HoR$e2024!eLk@sPh#ynX')

        # Definir query para buscar datos de los últimos 2 minutos
        query = {
            "query": {
                "range": {
                    "frame.frame_frame_time_utc": {
                        "gte": "now-2m/m",  # Mayor o igual a hace 2 minutos
                        "lte": "now"        # Menor o igual a ahora
                    }
                }
            }
        }

        # Realizar petición GET a Elasticsearch
        response = requests.get(SM_URL, headers=headers, auth=auth, json=query)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        # Retornar respuesta JSON de Elasticsearch
        return response.json()

    except Exception as e:
        # Propagar error como HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dnsAmplificationAttack", response_class=Response)
async def dns_amplification_attack(request: Request):
    """
    Procesa datos de ataques de amplificación DNS convirtiendo JSON a XML.
    
    PRE:
    - El request debe contener un JSON válido específico para ataques DNS
    - El JSON debe seguir la estructura esperada para modelos de amenaza DNS
    - La función json_to_xml debe poder procesar la estructura de datos
    
    POST:
    - Retorna una Response con el XML generado
    - El media_type de la respuesta es "application/xml"
    - El contenido XML sigue el formato de modelo de amenaza
    
    Funcionalidad:
    Especializada en procesar datos relacionados con ataques de amplificación DNS.
    Convierte los datos JSON recibidos a formato XML para su posterior procesamiento
    o almacenamiento en sistemas que requieren este formato.
    """
    # Extraer datos JSON del request
    data = await request.json()
    
    # Convertir JSON a XML usando la función auxiliar
    xml_str = json_to_xml(data)
    
    # Retornar XML como respuesta
    return Response(content=xml_str, media_type="application/xml")


@app.post("/ntpattack", response_class=Response)
async def ntp_attack(request: Request):
    """
    Procesa datos de ataques NTP convirtiendo JSON a XML.
    
    PRE:
    - El request debe contener un JSON válido específico para ataques NTP
    - El JSON debe seguir la estructura esperada para modelos de amenaza NTP
    - La función json_to_xml debe poder procesar la estructura de datos
    
    POST:
    - Retorna una Response con el XML generado
    - El media_type de la respuesta es "application/xml"
    - El contenido XML sigue el formato de modelo de amenaza
    
    Funcionalidad:
    Especializada en procesar datos relacionados con ataques NTP (Network Time Protocol).
    Convierte los datos JSON recibidos a formato XML manteniendo la estructura
    jerárquica necesaria para el análisis de este tipo de amenazas.
    """
    # Extraer datos JSON del request
    data = await request.json()
    
    # Convertir JSON a XML usando la función auxiliar
    xml_str = json_to_xml(data) 
    
    # Retornar XML como respuesta
    return Response(content=xml_str, media_type="application/xml")


import xml.etree.ElementTree as ET

def json_to_xml(data: dict) -> str:
    """
    Convierte una estructura de datos JSON a formato XML con soporte para atributos.
    
    PRE:
    - data debe ser un diccionario válido (dict)
    - La estructura debe tener al menos un elemento raíz
    - Las claves que empiezan con "_" o "-" se interpretan como atributos XML
    - Los valores pueden ser dict, list, str, int, float, bool o None
    
    POST:
    - Retorna una cadena (str) que contiene XML válido y bien formado
    - Incluye declaración XML con encoding UTF-8
    - Mantiene la jerarquía original de la estructura JSON
    - Los atributos se mapean correctamente a atributos XML
    """

    def is_attr(key: str) -> bool:
        """Determina si la clave representa un atributo XML."""
        return key.startswith("_") or key.startswith("-")

    def attr_name(key: str) -> str:
        """Convierte la clave JSON en nombre de atributo XML."""
        return key[1:] if is_attr(key) else key

    def create_element(parent, key, value):
        """Función recursiva para crear elementos XML."""
        if isinstance(value, dict):
            if is_attr(key):
                # Atributos del elemento padre
                for attr_key, attr_val in value.items():
                    if is_attr(attr_key):
                        parent.set(attr_name(attr_key), str(attr_val))
            else:
                # Crear subelemento
                elem = ET.SubElement(parent, key)
                for sub_key, sub_val in value.items():
                    create_element(elem, sub_key, sub_val)

        elif isinstance(value, list):
            for item in value:
                create_element(parent, key, item)

        else:
            if is_attr(key):
                parent.set(attr_name(key), str(value))
            else:
                elem = ET.SubElement(parent, key)
                elem.text = "" if value is None else str(value)

    # Elemento raíz
    root_tag = next(iter(data))
    root_content = data[root_tag]

    root = ET.Element(root_tag)

    for key, value in root_content.items():
        create_element(root, key, value)

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root, encoding="unicode")

    return xml_declaration + xml_body



