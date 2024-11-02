#!/usr/bin/python

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timezone
from dataclasses import dataclass

@dataclass
class Charge:
    identifier: str
    price: float
    start_dt: datetime

quarter_to_month = {
    'Q1': 1,   # January
    'Q2': 4,   # April
    'Q3': 7,   # July
    'Q4': 10   # October
}

def main():
    urls = [
        "https://www.ikb.at/energie/photovoltaik/einspeisevertrag"]

    for url in urls:
        response = requests.get(url)

        charges = []
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table with the specified ID
            table = soup.find('table', class_='contenttable')
            
            # Check if the table was found
            if table:
                # Extract data from the table
                rows = table.find_all('tr')
                
                # Print out the data from each row
                for row in rows:
                    columns = row.find_all(['th', 'td'])  # Get both headers and data cells
                    if len(columns) == 2:  # Ensure we have two columns
                        date_str = columns[0].get_text(strip=True)
                        
                        
                        quarter, year = date_str.split()
                        
                        # Convert the first column to datetime
                        try:
                            date = datetime(int(year), quarter_to_month.get(quarter), 1)
                        except ValueError:
                            print(f"Error parsing date: {date_str}")
                            continue
                        
                        price_str = columns[1].get_text(strip=True)
                        price_match = re.search(r'([\d,]+).*?', price_str)
                        try:
                            price_value = float(price_match.group(1).replace(',', '.'))
                        except ValueError:
                            print(f"Error converting price to float: {price_str}")
                            continue
                        
                    charges.append(Charge(identifier="feed-in", price=price_value, start_dt=date))
            else:
                print("Table with ID 'contenttable' not found.")
        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")


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
