import json
import JamfAPIClient as Japi

#API key
key = '7JM97TTS2AST6HQPAVX491V5N8WPDWED'
#Networkd ID
ID = '77385124'
#URL
jamf_url = 'https://itdynamicslabs.jamfcloud.com/api/'

deviceSN = 'HXJL5BWR1WFV'
#deviceUDID = '456297c4ca4205968711ec9c924ba78e8f2ede56'
outputFile = 'output.txt'

client = Japi.JamfAPIClient(jamf_url, ID, key)

