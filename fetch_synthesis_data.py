import requests
import json
import os
from datetime import datetime

# Crée le dossier de sortie s'il n'existe pas
OUTPUT_DIR = "C:/Users/SF96377/Desktop/hil_auto_kpi/data/synthesis_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# URLs à interroger
SIMPLE_ENDPOINTS = {
    "procedures": "http://10.32.132.219:8001/procedure-service/procedure/get",
    "kpi_variables": "http://10.32.132.219:8001/kpi-variable-service/kpi_variable/get?page=1&size=100",
    "comments": "http://10.32.132.219:8001/comment-service/comment/get?page=1&size=100"
}

PROCEDURE_DEFINITION_URLS = [
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00000146/7?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00000146/6?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00006238/10?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00000146/9?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00005864/2?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00001046/4?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00006237/5?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00007683/3?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00011553/2?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-definition/multiple_procedure_definition/get/TES-00006238/9?page=1&size=10"
]

PROCEDURE_DIGITALIZATION_URLS = [
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00000146/7?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00000146/6?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00006238/10?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00000146/9?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00005864/2?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00001046/4?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00006237/5?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00007683/3?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00011553/2?page=1&size=10",
    "http://10.32.132.219:8001/procedure-service/procedure-digitaliaztion/multiple_procedure_digitalization/get/TES-00006238/9?page=1&size=10"
]


def fetch_and_save(urls, output_filename, data_type):
    all_items = []

    if isinstance(urls, str):
        urls = [urls]

    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            json_data = response.json()
            items = json_data.get("items", [])
            for item in items:
                item["type"] = data_type
            all_items.extend(items)
        except Exception as e:
            print(f"Erreur lors de l'accès à {url} : {e}")

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"items": all_items}, f, ensure_ascii=False, indent=2)
        print(f"✅ Données sauvegardées dans {output_path} ({len(all_items)} items)")


if __name__ == "__main__":
    print(f"\n📥 Début de récupération : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Endpoints simples
    fetch_and_save(SIMPLE_ENDPOINTS["procedures"], "procedure.json", "procedure")
    fetch_and_save(SIMPLE_ENDPOINTS["kpi_variables"], "kpi_variable.json", "kpi_variable")
    fetch_and_save(SIMPLE_ENDPOINTS["comments"], "comment.json", "comment")

    # Multiples requêtes
    fetch_and_save(PROCEDURE_DEFINITION_URLS, "procedure_def.json", "procedure_definition")
    fetch_and_save(PROCEDURE_DIGITALIZATION_URLS, "procedure_digi.json", "procedure_digitalization")

    print(f"\n📦 Terminé.\n")
