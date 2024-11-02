#!/usr/bin/python

import requests
import json
from datetime import datetime
from datetime import timezone
from dataclasses import dataclass

@dataclass
class Charge:
    identifier: str
    price: float
    start_dt: datetime


def main():
    urls = [
        "https://sas.ikb.at/ws/strompreise.svc/GetWerteJSON?schluessel=com",
        "https://sas.ikb.at/ws/strompreise.svc/GetWerteJSON?schluessel=combu"]

    for url in urls:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.json())

        charges = []
        for entry in data.get("Werte"):
            charges.append(Charge(identifier=entry.get("schluessel"), price=float(entry.get("wert").replace(",", ".")), start_dt=datetime.strptime(entry.get("giltab"), "%d.%m.%Y")))

        influxdb_url = "http://192.168.178.26:8086/write?db=ikb"


        # Prepare and write each point to the database
        for charge in charges:
            line = f"charges,charge={charge.identifier} price={charge.price} {int(charge.start_dt.astimezone(timezone.utc).timestamp() * 1_000_000_000)}"
            response = requests.post(influxdb_url, data=line)
            
            if response.status_code == 204:
                print(f"{charge} written successfully.")
            else:
                print(f"Failed to write {charge}: {response.text}")

    print("Data written successfully")        

if __name__ == "__main__":
    main()
