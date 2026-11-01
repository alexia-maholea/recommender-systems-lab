import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import SetItemValues, Batch
from recombee_api_client.exceptions import APIException


import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = 'recommender-systems-dev'
PRIVATE_TOKEN = os.getenv("RECOMBEE_PRIVATE_TOKEN")
REGION = Region.EU_WEST

client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=REGION)

PATH_DATASET = 'IMDb_All_Genres_etf_clean1.csv' 

def parse_gross(value):
    value = str(value).strip()
    if not value.startswith("$"):
        return None  # ex. "Gross Unkown"
    value = value[1:]
    multiplier = 1
    if value.endswith("M"):
        multiplier, value = 1_000_000, value[:-1]
    elif value.endswith("K"):
        multiplier, value = 1_000, value[:-1]
    return float(value.replace(",", "")) * multiplier



def send_items():
    """Functie care citeste dataset-ul si trimite item-urile in Recombee"""
    df = pd.read_csv(PATH_DATASET)
    print(f"Se trimit {len(df)} item-uri in Recombee...")
    
    requests = []
    
    for index, row in df.iterrows():
        item_id = f"movie_{index}"
        
        properties = {
            "Movie_Title": str(row["Movie_Title"]),
            "Year": int(row["Year"]),
            "Director": str(row["Director"]),
            "Actors": str(row["Actors"]),
            "Rating": float(row["Rating"]),
            "main_genre": str(row["main_genre"]),
            "side_genre": str(row["side_genre"]),
            "Runtime_Mins": int(row["Runtime(Mins)"]),
            "Censor": str(row["Censor"]),
            "Total_Gross": parse_gross(row["Total_Gross"])
        }
        
        # Adaugam request-ul de setare a valorilor pentru item
        # (SetItemValues creează automat item-ul dacă acesta nu există)
        requests.append(SetItemValues(item_id, properties, cascade_create=True))
        
        # Trimitem in loturi (batch) de cate 100 pentru eficienta
        if len(requests) == 100:
            client.send(Batch(requests))
            requests = []
            print("S-a trimis un lot de 100 item-uri...")
            
    # Trimitem si restul ramanase (daca numarul total nu e multiplu de 100)
    if requests:
        client.send(Batch(requests))
        print("S-a trimis ultimul lot de item-uri.")
        
    print("Toate item-urile au fost trimise cu succes!")

if __name__ == "__main__":
    send_items()
