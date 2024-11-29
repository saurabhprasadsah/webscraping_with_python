import requests
from bs4 import BeautifulSoup
import re

def extract_medicine_data(html):
    """
    Extracts the medicine name, brand name, and 'Contains' field from the HTML using BeautifulSoup.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Extract medicine name
        medicine_name_elements = soup.find_all(class_=re.compile(r"MedicineOverviewSection_medicineName__\w+"))
        medicine_name = "N/A"
        if medicine_name_elements:
            medicine_name = medicine_name_elements[0].get_text(strip=True)
            print(f"Medicine Name found: {medicine_name}")
        else:
            print("Medicine Name not found.")

        # Extract brand name
        brand_name_elements = soup.find_all(class_=re.compile(r"MedicineOverviewSection_brandName__\w+"))
        brand_name = "N/A"
        if brand_name_elements:
            brand_name = brand_name_elements[0].get_text(strip=True)
            print(f"Brand Name found: {brand_name}")
        else:
            print("Brand Name not found.")

        # Extract "Contains" field from the DescriptionTable section
        contains_value = "N/A"
        description_table_rows = soup.find_all("tr")

        # Debugging: Print the first 5 rows of the table to check structure
        print("Debugging DescriptionTable rows:")
        for row in description_table_rows[:5]:
            print(row.prettify())  # Printing the first 5 rows for debugging

        for row in description_table_rows:
            field = row.find("td", class_=re.compile(r"DescriptionTable_field__\w+"))
            value = row.find("td", class_=re.compile(r"DescriptionTable_value__\w+"))
            
            if field and value:
                field_text = field.get_text(strip=True)
                value_text = value.get_text(strip=True)
                
                if field_text == "Contains":
                    contains_value = value_text
                    print(f"Contains value found: {contains_value}")
                    break  # Exit the loop once we've found the "Contains" value

        return {
            "Medicine Name": medicine_name,
            "Brand Name": brand_name,
            "Contains": contains_value,
        }
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def fetch_data_from_url(url):
    """
    Fetches the HTML content from the given URL and extracts data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except Exception as e:
        print(f"Failed to fetch URL: {url}, Error: {e}")
        return None

def process_csv(input_csv, output_csv):
    """
    Processes the input CSV file, fetches data for each URL, and writes the results to the output CSV.
    """
    import csv
    
    with open(input_csv, mode="r", newline="", encoding="utf-8") as infile, \
         open(output_csv, mode="w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Medicine Name", "Brand Name", "Contains"]  # Add new fields to CSV
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for row in reader:
            url = row["URL"]
            print(f"[{row['SKU']}] Fetching data for URL: {url}")

            html = fetch_data_from_url(url)
            if html:
                medicine_data = extract_medicine_data(html)
                if medicine_data:
                    row.update(medicine_data)  # Add new fields to the row
                    writer.writerow(row)  # Write the updated row to the output CSV
                else:
                    print(f"Failed to extract data for {url}. Error logged.")
                    writer.writerow(row)  # Write the row even if no data was extracted

# Example of calling the process_csv function
input_csv = "HARSHITA.csv"  # Replace with your actual CSV file path
output_csv = "output_data.csv"  # The file where results will be written
process_csv(input_csv, output_csv)