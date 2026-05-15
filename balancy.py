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

# ✅ FIX 1: Use the main Balancy domain for CMS/Management
#CMS_URL = "https://balancy.dev/api"
CMS_URL='https://us-central1-balancy.cloudfunctions.net/api'

# ✅ FIX 2: S2S URL (Confirmed working by your 403 error earlier)
S2S_URL = "https://s2s.balancy.dev/v1"


class BalancyAutomator:
    def __init__(self):
        self.project_id = PROJECT_ID
        self.public_key = PUBLIC_KEY
        self.private_key = PRIVATE_KEY

    # --- SIGNATURE LOGIC 1: CMS (Management) ---
    def _generate_cms_signature(self, payload_str, nonce, timestamp):
        # CMS format: timestamp + \n + nonce + \n + payload + \n (Trailing Newline)
        data_to_sign = f"{timestamp}\n{nonce}\n{payload_str}\n"
        return hmac.new(
            self.private_key.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    # --- SIGNATURE LOGIC 2: S2S (Runtime) ---
    def _generate_s2s_signature(self, payload_str, nonce, timestamp):
        # S2S format: timestamp + \n + nonce + \n + project_id + \n + payload (NO Trailing Newline)
        # Matches your working CURL snippet
        data_to_sign = f"{timestamp}\n{nonce}\n{self.project_id}\n{payload_str}"
        return hmac.new(
            self.private_key.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _make_cms_request(self, method, endpoint, data=None):
        """
        SCENARIO 1 & 3: Management API (Creating Overrides)
        """
        url = f"{CMS_URL}{endpoint}"
        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time()))  # Seconds for CMS

        # CMS always expects JSON body in signature
        payload_json = json.dumps(data) if data is not None else "{}"

        signature = self._generate_cms_signature(payload_json, nonce, timestamp)

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
            # Retry with project ID in path if 404
            if response.status_code == 404 and "/projects/" not in url:
                print("⚠️ 404, retrying with Project ID path...")
                return self._make_cms_request(method, f"/projects/{self.project_id}{endpoint}", data)
            raise Exception(f"CMS Error {response.status_code}: {response.text}")
        return response.json()

    def _make_s2s_request(self, method, endpoint):
        """
        SCENARIO 2: Runtime API (Looking up Users)
        """
        url = f"{S2S_URL}{endpoint}"

        nonce = uuid.uuid4().hex[:32]  # 32 hex chars
        timestamp = str(int(time.time() * 1000))  # Milliseconds for S2S

        # For GET, payload is "{}"
        json_data = "{}"

        signature = self._generate_s2s_signature(json_data, nonce, timestamp)

        print(f"🕵️ S2S Request: {method} {url}")

        headers = {
            "accept": "*/*",
            "Balancy-Signature": signature,
            "Balancy-Timestamp": timestamp,
            "Balancy-Nonce": nonce
        }

        # S2S GET requests send headers but NO body data
        response = requests.request(method, url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"S2S Error {response.status_code}: {response.text}")

        return response.json()

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
            # Try specific project endpoint first
            response = self._make_cms_request("POST", f"/projects/{self.project_id}/overrides", payload)
            new_id = response.get('id')
            print(f"✅ Success! Override Created. ID: {new_id}")
            return new_id
        except Exception as e:
            print(f"❌ Creation Failed: {e}")
            return None

    # --- SCENARIO 2: GET DEVICE ID ---
    def scenario_2_get_device_id(self, user_id):
        print(f"\n--- SCENARIO 2: Searching Device ID for User {user_id} ---")

        # Endpoint: /games/{gameId}/envs/0/users/{userId}
        endpoint = f"/games/{self.project_id}/envs/0/users/{user_id}"

        try:
            response = self._make_s2s_request("GET", endpoint)

            # Look for DeviceId
            general_info = None
            if isinstance(response, dict):
                if "GeneralInfo" in response:
                    general_info = response["GeneralInfo"]
                elif "system" in response and "GeneralInfo" in response["system"]:
                    general_info = response["system"]["GeneralInfo"]
                elif "value" in response and "GeneralInfo" in response["value"]:
                    general_info = response["value"]["GeneralInfo"]

            if general_info and "DeviceId" in general_info:
                d_id = general_info["DeviceId"]
                print(f"✅ Found Device ID: {d_id}")
                return d_id

            print(f"⚠️ Device ID not found. Response keys: {list(response.keys())}")
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

    # --- CONFIG ---
    TARGET_ENV = "development"
    TARGET_BRANCH = "v1.11.0"

    # IDs
    MY_OVERRIDE_ID = "YOUR_OVERRIDE_ID_HERE"
    ROYAL_TOURNAMENT_ID = "35341"
    NEW_YEARS_ID = "40911"

    # --- DATA ---
    device_list = [
        "C295AC8C-9D54-4E06-83DD-E6C69D6C9D6C",
        "c476112fcf6afcb014032f141e0d97db",
        "82D4AA13-E79C-4D35-BD49-FABE9733",
        "29645916-B74C-43D4-96F2-9D7A8F5D4",
        "E76F99F5-A150-43EA-9EE8-CA1586EDD",
        "7BEDA0E0-AE89-43C4-8E05-2C9217C82",
        "2A2DB4FE-32CD-42DB-88DA-AD16CAC",
        "467E7D7F-0CFA-4FC6-A82E-F1D8EA38C",
        "66943FD3-B877-4841-BDDC-469C27D5"
    ]

    full_override_docs = [
        {"documentId": "3256", "parameter": "Trophy Settings", "value": "Open"},
        {"documentId": "4056", "parameter": "Prize Ladder Settings", "value": "Open"},
        {"documentId": "28562", "parameter": "Prize Ladder Settings", "value": "Open"},
        {"documentId": "28683", "parameter": "Prize Ladder Settings", "value": "Open"},
        {"documentId": "25763", "parameter": "Jigsaw Rewards", "value": "Open"},
        {"documentId": "3741", "parameter": "Purchase Method", "value": "31032"},
        {"documentId": ROYAL_TOURNAMENT_ID, "parameter": "Condition", "value": "Open"},
        {"documentId": "30884", "parameter": "Settings", "value": "Open"},
        {"documentId": "26597", "parameter": "Unlock At", "value": 6},
        {"documentId": NEW_YEARS_ID, "parameter": "Condition", "value": "Open"}
    ]

    # --- EXECUTE ---

    # 1. CREATE (Uncomment to run)
    created_id = bot.scenario_1_create_override("Automation Override-New", device_list, full_override_docs)
    print(f"SAVE THIS ID: {created_id}")

    # 2. UPDATE USER & DEPLOY (Uncomment to run)
    # target_user = "89421c3c-ba66-11f0-85c0-1fec53a055ba"
    # dev_id = bot.scenario_2_get_device_id(target_user)

    # if dev_id and MY_OVERRIDE_ID != "YOUR_OVERRIDE_ID_HERE":
    #     bot.scenario_3_update_and_deploy(MY_OVERRIDE_ID, dev_id, TARGET_ENV, TARGET_BRANCH)