#Jamf API Interface Class
import base64
import json
import requests
from requests.auth import HTTPBasicAuth
from typing import Any, Dict, Optional

#Curtesy of ChatGPT and Sean M

class JamfAPIClient:
    """
    Simple Jamf API client for device operations.
    Assumes jamf_url, ID, and key are provided at init.
    """

    device_dictionary = {}
    location_dictionary = {}

    def __init__(self, jamf_url: str, username: str, password: str, timeout: float = 10.0):
        self.jamf_url = jamf_url.rstrip('/') + '/'
        self.auth = HTTPBasicAuth(username, password)
        self.timeout = timeout
        self.createDeviceUDIDdict()
        self.mapLocations()
        self.mapDevicesToLocations()
        print("Initialised.")

    def mapLocations(self):
        """
        GET all locations and map them
        """
        print("Mapping all locations's id's -> Location Names...")
        print("    Getting all locations...", end='')
        resp = requests.get(
            f'{self.jamf_url}locations/',
            auth=self.auth,
            timeout=self.timeout
        )
        print("    Done.")
        print("    Creating dictionary...", end='')
        resp.raise_for_status()
        response = resp.json()
        for location in response["locations"]:
            self.location_dictionary[location["id"]] = location["name"]
        print("    Done.")
        print("    Writing output...", end='')
        with open("LocationDict.json", 'w') as f:
            f.write(json.dumps(self.location_dictionary, indent=4))
        print("    Done.")
        print()

    def createDeviceUDIDdict(self):
        """
        GET all devices and map them
        """
        print("Mapping all device's Serial Numbers -> UDIDs...")
        print("    Getting all devices...", end='')
        allDevices = self.get_devices()["devices"]
        print("    Done.")
        print("    Creating Dicionary...", end='')
        deviceDict = {}
        for device in allDevices:
            deviceDict[device["serialNumber"]] = device["UDID"]
        print("    Done.")
        print("    Writing output...", end='')
        self.device_dictionary = deviceDict
        with open("DeviceDict.json", 'w') as f:
            f.write(json.dumps(self.device_dictionary, indent=4))
        print("    Done.")
        print()

    def mapDevicesToLocations(self):
        "This will order the devices by location"
        mappedDevices = {}
        print("Mapping devices to locations")
        for locationID in self.location_dictionary.keys():
            locationName = self.location_dictionary[locationID]
            print(F"    getting devices for {locationName}")
            devices = self.get_devices(locationID)["devices"]
            d = {}
            for device in devices:
                d[device["UDID"]] = {
                    "name" : device["name"],
                    "serialNumber" : device["serialNumber"],
                    "class" : device["class"]
                }
            mappedDevices[locationName] = d
            print("    Done.")

        print("    Writing output...", end='')
        with open("DeviceLocationDict.json", 'w') as f:
            f.write(json.dumps(mappedDevices, indent=4))
        print("    Done.")
        print()
            
        

## will replace the curren notes in the device with specified onces
    def replace_device_notes(self, udid: str, notes: str) -> dict:
        """
        POST updated device details (notes).
        """
        data = {
            'udid': udid,
            'notes': notes
        }
        resp = requests.post(
            f'{self.jamf_url}devices/{udid}/details',
            auth=self.auth,
            json=data,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

##Will update the notes on a new line below the old ones
    #Error Handling from Chat GPT
    def update_device_notes(self, udid: str, notes: str) -> dict:
        """
        Returns dict: {
          "ok": bool,
          "status_code": Optional[int],
          "error": Optional[str],
          "response": Optional[Any]
        }
        """
        dev_res = self.get_device(udid)
        if not dev_res.get("ok"):
            return {"ok": False, "status_code": dev_res.get("status_code"), "error": f"get_device failed: {dev_res.get('error')}", "response": dev_res.get("response")}

        dev = {"device": dev_res["device"]}  # keep original shape for compatibility
        if "notes" not in dev["device"]:
            return {"ok": False, "status_code": None, "error": "Unexpected get_device response structure", "response": dev}

        old = dev["device"]["notes"] or ""
        data = {"udid": udid, "notes": f"{old}\n\nFrom API Client:\n{notes}"}
        url = f"{self.jamf_url.rstrip('/')}/devices/{udid}/details"

        try:
            resp = requests.post(url, auth=self.auth, json=data, timeout=self.timeout)
        except requests.Timeout as e:
            return {"ok": False, "status_code": None, "error": f"timeout: {e}", "response": None}
        except requests.ConnectionError as e:
            return {"ok": False, "status_code": None, "error": f"connection error: {e}", "response": None}
        except requests.RequestException as e:
            return {"ok": False, "status_code": None, "error": f"request exception: {e}", "response": None}

        status = resp.status_code
        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        if 200 <= status < 300:
            return {"ok": True, "status_code": status, "error": None, "response": body}

        # Non-2xx responses returned for external handling
        return {"ok": False, "status_code": status, "error": None, "response": body}

    def get_device(self, udid: str, include_apps: bool = False) -> Dict[str, Any]:
        """
        Return either {'ok': True, 'device': {...}}
        or {'ok': False, 'status_code': Optional[int], 'error': Optional[str], 'response': Optional[Any]}
        so callers can handle uniformly.
        """
        params = {'includeApps': 'true' if include_apps else 'false'}
        url = f"{self.jamf_url.rstrip('/')}/devices/{udid}"
        #return error if we have a blank string otherwise Jamf gets all devices
        if udid == "":
            return {"ok": False, "status_code": None, "error": "UDID cannot be blank", "response": None}
        
        try:
            resp = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        except requests.Timeout as e:
            return {"ok": False, "status_code": None, "error": f"timeout: {e}", "response": None}
        except requests.ConnectionError as e:
            return {"ok": False, "status_code": None, "error": f"connection error: {e}", "response": None}
        except requests.RequestException as e:
            return {"ok": False, "status_code": None, "error": f"request exception: {e}", "response": None}

        status = resp.status_code
        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        if 200 <= status < 300:
            # ensure the successful shape contains 'device' to match callers' checks
            if isinstance(body, dict) and "device" in body:
                return {"ok": True, "device": body["device"]}
            return {"ok": False, "status_code": status, "error": "missing 'device' key", "response": body}

        return {"ok": False, "status_code": status, "error": None, "response": body}


    def get_devices(self, filterLocation: str = "") -> dict:
        """
        GET list of devices.
        """
        params = {'location': filterLocation if filterLocation != "" else None}
        resp = requests.get(
            f'{self.jamf_url}devices',
            auth=self.auth,
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()
