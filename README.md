# JAMF-API-Connector
This script has two parts. 
1. A python library that interface with the JAMF API: JamfAPIClient.py
2. A script which uses this library to pass notes from a CSV file to devices in JAMF.

The Jamf API Client will create a dectioanry for translating serial numbers => udid codes. This is needed as JAMF doesn't support searching by serial number just yet. When you want to get a device using a serial number, pelase use this translation table to get the udid first.

The CSV script will create a log file called output.log 
