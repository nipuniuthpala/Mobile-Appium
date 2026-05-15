import base64
import time
import uuid
import json
import hmac
import hashlib
import requests

# --- CONFIGURATION ---
PROJECT_ID = "1cb7879e-9aa2-11ef-90be-066676c39f77"
PUBLIC_KEY = "MDBlNGYyMDI1N2MyNWNiOWFkZmU3MW"
PRIVATE_KEY = "YzJiYzM3YWQwNjExNDgyZTc0NWRkYT"

# URL 1: Management (Creating Overrides/Deploying)
CMS_URL = "https://data-editor.balancy.dev/api"

# URL 2: Runtime S2S (Looking up Users)
S2S_URL = "https://s2s.balancy.dev/v1"


class BalancyAutomator:
    def __init__(self):
        self.project_id = PROJECT_ID
        self.public_key = PUBLIC_KEY
        self.private_key = PRIVATE_KEY

    def _generate_signature(self, payload, nonce, timestamp):
        data_to_sign = f"{timestamp}\n{nonce}\n{payload}\n"
        return hmac.new(
            self.private_key.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _make_cms_request(self, method, endpoint, data=None):
        """ SCENARIO 1 & 3: Management API (Uses X- Headers) """
        url = f"{CMS_URL}{endpoint}"
        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time()))  # Seconds

        # CMS always expects JSON body in signature
        payload_json = json.dumps(data) if data is not None else "{}"

        signature = self._generate_signature(payload_json, nonce, timestamp)

        headers = {
            "Content-Type": "application/json",
            "X-Project-Id": self.project_id,
            "X-Public-Key": self.public_key,
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Signature": signature
        }

        print(f"📡 CMS Request: {method} {url}")
        response = requests.request(method, url, headers=headers, data=payload_json)

        if response.status_code not in [200, 201]:
            if response.status_code == 404 and "/projects/" not in url:
                return self._make_cms_request(method, f"/projects/{self.project_id}{endpoint}", data)
            raise Exception(f"CMS Error {response.status_code}: {response.text}")
        return response.json()
    '''
    def _make_s2s_request(self, method, endpoint):
        url = f"{S2S_URL}{endpoint}"
        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time() * 1000))  # milliseconds
        payload = "{}"  # required for GET

        # ✅ INCLUDE game_id in the signature
        data_to_sign = f"{timestamp}\n{nonce}\n{self.project_id}\n{payload}\n"

        signature = hmac.new(
            self.private_key.encode("utf-8"),
            data_to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "accept": "*/*",
            "Balancy-Signature": signature,
            "Balancy-Timestamp": timestamp,
            "Balancy-Nonce": nonce,
            "Balancy-Game-Private-Key": self.private_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"S2S Error {response.status_code}: {response.text}")

        return response.json()
    '''

    def _make_s2s_request(self, method, endpoint):
        url = f"{S2S_URL}{endpoint}"

        nonce = uuid.uuid4().hex[:32]  # must be 32 hex chars
        timestamp = str(int(time.time() * 1000))  # milliseconds

        # JSON_data for GET must be {}
        json_data = "{}"

        # S2S signature string per docs
        data_to_sign = f"{timestamp}\n{nonce}\n{self.project_id}\n{json_data}"

        signature = hmac.new(
            self.private_key.encode("utf-8"),
            data_to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        print("🔐 DATA TO SIGN:", repr(data_to_sign))
        print("🔐 GENERATED SIGNATURE:", signature)

        headers = {
            "accept": "*/*",
            "Balancy-Signature": signature,
            "Balancy-Timestamp": timestamp,
            "Balancy-Nonce": nonce
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"S2S Error {response.status_code}: {response.text}")

        return response.json()

    '''
    # --- SCENARIO 1: CREATE OVERRIDE ---
    def scenario_1_create_override(self, name, initial_device_ids, override_docs):
        print(f"\n--- SCENARIO 1: Creating Override '{name}' ---")

        conditions = []
        for did in initial_device_ids:
            conditions.append({
                "path": "System.GeneralInfo.DeviceId",
                "operator": "Equal",
                "value": did
            })

        payload = {
            "name": name,
            "isActive": True,
            "priority": 100,
            "conditions": {"operator": "Or", "childs": conditions},
            "overrides": override_docs
        }

        try:
            response = self._make_cms_request("POST", f"/projects/{self.project_id}/overrides", payload)
            new_id = response.get('id')
            print(f"✅ Success! Override Created. ID: {new_id}")
            return new_id
        except Exception as e:
            print(f"❌ Creation Failed: {e}")
            return None
    '''
    # --- SCENARIO 2: FIND DEVICE ID ---
    def scenario_2_get_device_id(self, user_id):
        print(f"\n--- SCENARIO 2: Searching Device ID for User {user_id} ---")
        endpoint = f"/games/{self.project_id}/envs/0/users/{user_id}"

        try:
            response = self._make_s2s_request("GET", endpoint)

            # ✅ This endpoint ONLY returns user id
            if isinstance(response, dict) and "id" in response:
                print(f"✅ User exists. User ID: {response['id']}")
                return response["id"]

            print(f"⚠️ Unexpected response structure: {response}")
            return None

        except Exception as e:
            print(f"❌ Failed to fetch profile: {e}")
            return None

    def scenario_5_post_deploy(self):

        endpoint = f"/games/{self.project_id}/branches/dev/dev_1.11.0/deploy"

        try:
            response = self._make_s2s_request("POST", endpoint)

            # ✅ This endpoint ONLY returns user id

            print(f"✅ deployed: {response}")
            return response

            print(f"⚠️ Unexpected response structure: {response}")
            return None

        except Exception as e:
            print(f"❌ Failed to fetch profile: {e}")
            return None

    # --- SCENARIO 3: UPDATE & DEPLOY ---
    def scenario_3_update_and_deploy(self, override_id, new_device_id, target_env, target_branch):
        print(f"\n--- SCENARIO 3: Updating & Deploying ---")
        if not new_device_id: return

        # 1. Get (CMS)
        try:
            current_data = self._make_cms_request("GET", f"/projects/{self.project_id}/overrides/{override_id}")
        except:
            current_data = self._make_cms_request("GET", f"/overrides/{override_id}")

        existing_childs = current_data.get('conditions', {}).get('childs', [])

        if any(c.get('value') == new_device_id for c in existing_childs):
            print("⚠️ Device ID already exists. Skipping update.")
        else:
            existing_childs.append({
                "path": "System.GeneralInfo.DeviceId",
                "operator": "Equal",
                "value": new_device_id
            })
            current_data['conditions']['childs'] = existing_childs

            # 2. Put (CMS)
            self._make_cms_request("PUT", f"/projects/{self.project_id}/overrides/{override_id}", current_data)
            print(f"✅ Override updated with Device ID: {new_device_id}")

        # 3. Deploy (CMS)
        deploy_payload = {
            "environment": target_env,
            "branch": target_branch,
            "comment": f"Auto-deploy: Added device {new_device_id}"
        }
        self._make_cms_request("POST", f"/projects/{self.project_id}/deploy", deploy_payload)
        print("✅ Deployment Triggered.")


# --- EXECUTION ---
if __name__ == "__main__":
    bot = BalancyAutomator()

    # INPUTS
    user_id = "14347e8b-dbf9-11f0-a547-1fec53a055ba"

    # 1. RUN SCENARIO 2 (Test User Lookup)
    found_device = bot.scenario_2_get_device_id(user_id)
    deploy=(bot.scenario_5_post_deploy())

    # 2. RUN SCENARIO 3 (Uncomment and fill ID to run)
    # MY_OVERRIDE_ID = "YOUR_OVERRIDE_ID_HERE"
    # if found_device and MY_OVERRIDE_ID:
    #     bot.scenario_3_update_and_deploy(MY_OVERRIDE_ID, found_device, "development", "v1.11.0")