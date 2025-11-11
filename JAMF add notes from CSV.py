import json
import JamfAPIClient as Japi
from datetime import datetime
import logging
import csv

#API key
key = '7JM97TTS2AST6HQPAVX491V5N8WPDWED'
#Networkd ID
ID = '77385124'
#URL
jamf_url = 'https://itdynamicslabs.jamfcloud.com/api/'
#output file
outputFile = 'output.log'
#CSV file
csvFile = 'deviceList.csv'

print(f"output to:        {outputFile}")
print(f"Jamf URL:       {jamf_url}")

logging.basicConfig(
    filename=outputFile,
    filemode="a",               # append
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize fieldnames to expected keys
        rows = []
        for r in reader:
            rows.append({
                "Serial Number": r.get("SerialNumber") or r.get("serial_number") or r.get("Serial_Number"),
                "Notes": r.get("Notes") or r.get("notes")
            })
    return rows

##Start of script------------------------------------------------------------------------------------------------------------------------------
with open('output.json', 'w') as file:
    client = Japi.JamfAPIClient(jamf_url, ID, key)
    response = client.get_devices()
    file.write(json.dumps(response, indent=4))
    

exit(0)
logging.info("Script Started.")
logging.info("Current date: %s", datetime.now().date())

#connect to the Jamf API, this updates the list of serial number/ UDIDs as well
logging.info(f"Connecting to JAMF API {jamf_url}")
client = Japi.JamfAPIClient(jamf_url, ID, key)

logging.info(f"Collecting devices from {csvFile}")
records = load_csv(csvFile)

logging.info(f"updating device notes for {len(records)} devices")
for device in records:
    logging.info(f"    updating device: {device['Serial Number']}")
    try:
        udid = client.device_dictionary[device["Serial Number"]]
    except:
        udid = None
        #logging.error("    Device update failed!")
        #logging.error(f"    could not find device {device['Serial Number']}")
    response = client.update_device_notes(udid, device["Notes"])
    if not response["ok"]:
        logging.error("    device update failed!")
        logging.error(f"""
    OK:             {response['ok']}
    Status:        {response['status_code']}
    Error:          {response['error']}
    Response:  {response['response']}
    """)
    else:
        logging.info(f"    successfully added notes: {device['Notes']}")
logging.info("Script Ended.")
    
