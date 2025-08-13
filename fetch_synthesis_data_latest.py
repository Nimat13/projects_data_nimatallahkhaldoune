import requests
import csv
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

# Mapping des champs à exporter pour chaque type
FIELD_MAPPING = {
    "procedure": ["id", "reference", "revision", "status"],
    "comment": ["id", "info", "warning", "error"],
    "kpi_variable": ["id", "name", "value", "group_type", "references"],
    "procedure_definition": [
        "id", "created_at", "updated_at",
        "total_testruns[value]", "total_empty_testruns[value]", 
        "total_steps[value]", "total_AC[value]", "total_CO[value]", 
        "total_ER[value]", "procedure_id[reference]", 
        "procedure_id[revision]", "procedure_id[status]",
        "comment_id[info]", "comment_id[warning]", "comment_id[error]"
    ],
    "procedure_digitalization": [
        "id", "created_at", "updated_at",
        "total_testruns_digitalized[value]", "total_AC_digitalized[value]",
        "total_ER_digitalized[value]", "total_IC_digitalized[value]",
        "total_CO_digitalized[value]", "procedure_id[reference]",
        "procedure_id[revision]", "procedure_id[status]",
        "comment_id[info]", "comment_id[warning]", "comment_id[error]"
    ]
}

def get_nested_value(item, key):
    """Récupère une valeur imbriquée en utilisant la notation avec crochets"""
    if '[' in key:
        main_key, sub_key = key.split('[')
        sub_key = sub_key.rstrip(']')
        return str(item.get(main_key, {}).get(sub_key, ""))
    return str(item.get(key, ""))

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
            all_items.extend(items)
        except Exception as e:
            print(f"Erreur lors de l'accès à {url} : {e}")

    output_path = os.path.join(OUTPUT_DIR, output_filename.replace('.json', '.csv'))
    fields = FIELD_MAPPING.get(data_type, [])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Écrit les données
        for item in all_items:
            row = [get_nested_value(item, field) for field in fields]
            writer.writerow(row)
        
        # Ajoute la ligne de commentaire avec les en-têtes
        writer.writerow([f"#{','.join(fields)}"])
    
    print(f"✅ Données sauvegardées dans {output_path} ({len(all_items)} items)")

if __name__ == "__main__":
    print(f"\n📥 Début de récupération : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Endpoints simples
    fetch_and_save(SIMPLE_ENDPOINTS["procedures"], "procedure.csv", "procedure")
    fetch_and_save(SIMPLE_ENDPOINTS["kpi_variables"], "kpi_variable.csv", "kpi_variable")
    fetch_and_save(SIMPLE_ENDPOINTS["comments"], "comment.csv", "comment")

    # Multiples requêtes
    fetch_and_save(PROCEDURE_DEFINITION_URLS, "procedure_def.csv", "procedure_definition")
    fetch_and_save(PROCEDURE_DIGITALIZATION_URLS, "procedure_digi.csv", "procedure_digitalization")

    print(f"\n📦 Terminé.\n")