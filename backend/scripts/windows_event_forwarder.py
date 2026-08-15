import os
import sys
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("secureops.event_forwarder")

API_BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{API_BASE_URL}/api/auth/login"
EVENTS_ENDPOINT = f"{API_BASE_URL}/api/events"

# We will use the default seeded analyst account to authenticate
USERNAME = "analyst"
PASSWORD = "SecureOps2024!"

class SecureOpsClient:
    def __init__(self):
        self.token = None
        self.headers = {}

    def login(self):
        logger.info(f"Authenticating with SecureOps API at {LOGIN_ENDPOINT}...")
        try:
            # Send username/password as form data
            response = requests.post(
                LOGIN_ENDPOINT,
                data={"username": USERNAME, "password": PASSWORD},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                logger.info("Authentication successful!")
                return True
            else:
                logger.error(f"Authentication failed (HTTP {response.status_code}): {response.text}")
                return False
        except Exception as e:
            logger.error(f"Connection to SecureOps API failed: {e}")
            return False

    def send_event(self, event_data):
        if not self.token:
            if not self.login():
                return False

        try:
            response = requests.post(EVENTS_ENDPOINT, json=event_data, headers=self.headers, timeout=5)
            if response.status_code == 401:
                logger.warning("Token expired. Re-authenticating...")
                if self.login():
                    response = requests.post(EVENTS_ENDPOINT, json=event_data, headers=self.headers, timeout=5)
                else:
                    return False
            
            if response.status_code == 201:
                logger.info(f"Successfully forwarded event: {event_data['event_type']} (Source: {event_data['source_ip'] or 'local'})")
                return True
            else:
                logger.error(f"Failed to send event (HTTP {response.status_code}): {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending event to SecureOps: {e}")
            return False

try:
    import win32evtlog
except ImportError:
    logger.error("Could not import win32evtlog. Please run 'pip install pywin32' inside the venv.")
    sys.exit(1)

def process_and_forward_event(event, client):
    event_id = event.EventID & 0xFFFF
    event_time = event.TimeGenerated
    
    # We only care about specific Windows Security event IDs
    # 4625: Failed Logon
    # 4624: Successful Logon
    # 4720: User Account Created
    # 4732: Member Added to Local Group
    
    if event_id not in [4624, 4625, 4720, 4732]:
        return

    inserts = event.StringInserts
    if not inserts:
        return

    event_type = None
    description = None
    severity = None
    raw_data = {
        "event_id": event_id,
        "record_number": event.RecordNumber,
        "source_name": event.SourceName,
        "time_generated": event_time.isoformat()
    }
    source_ip = None
    destination_ip = None

    try:
        if event_id == 4625:  # Failed Logon
            # StringInserts indexes:
            # 5: TargetUserName
            # 6: TargetDomainName
            # 10: LogonType
            # 19: IpAddress (source IP)
            username = inserts[5] if len(inserts) > 5 else "Unknown"
            domain = inserts[6] if len(inserts) > 6 else "Unknown"
            logon_type = inserts[10] if len(inserts) > 10 else "Unknown"
            ip_address = inserts[19] if len(inserts) > 19 else None
            
            if ip_address and ip_address != "-" and ip_address != "127.0.0.1":
                source_ip = ip_address
            
            event_type = "failed_login"
            description = f"Real Windows Logon Failure: Account '{username}' on domain '{domain}'. Logon Type: {logon_type}."
            severity = "high"
            raw_data.update({
                "username": username,
                "domain": domain,
                "logon_type": logon_type,
                "source_ip": ip_address
            })

        elif event_id == 4624:  # Successful Logon
            # StringInserts indexes:
            # 5: TargetUserName
            # 6: TargetDomainName
            # 8: LogonType
            # 18: IpAddress (source IP)
            username = inserts[5] if len(inserts) > 5 else "Unknown"
            domain = inserts[6] if len(inserts) > 6 else "Unknown"
            logon_type = inserts[8] if len(inserts) > 8 else "Unknown"
            ip_address = inserts[18] if len(inserts) > 18 else None
            
            if ip_address and ip_address != "-" and ip_address != "127.0.0.1":
                source_ip = ip_address

            # Ignore background system logins to avoid noise
            if username.endswith("$") or username.lower() in ["system", "local service", "network service", "anonymous logoff"]:
                return

            event_type = "successful_login"
            description = f"Real Windows Logon Success: Account '{username}' on domain '{domain}'. Logon Type: {logon_type}."
            severity = "low"
            raw_data.update({
                "username": username,
                "domain": domain,
                "logon_type": logon_type,
                "source_ip": ip_address
            })

        elif event_id == 4720:  # User Account Created
            new_user = inserts[0] if len(inserts) > 0 else "Unknown"
            domain = inserts[1] if len(inserts) > 1 else "Unknown"
            creator = inserts[4] if len(inserts) > 4 else "Unknown"

            event_type = "privilege_change"
            description = f"Real Windows User Account Created: User '{new_user}' created by '{creator}'."
            severity = "medium"
            raw_data.update({
                "new_username": new_user,
                "domain": domain,
                "created_by": creator
            })

        elif event_id == 4732:  # Member Added to Local Group
            member = inserts[1] if len(inserts) > 1 else "Unknown"
            group_name = inserts[2] if len(inserts) > 2 else "Unknown"
            admin = inserts[6] if len(inserts) > 6 else "Unknown"

            event_type = "privilege_change"
            description = f"Real Windows Group Membership Change: User '{member}' added to group '{group_name}' by '{admin}'."
            
            if "admin" in group_name.lower():
                severity = "critical"
            else:
                severity = "medium"

            raw_data.update({
                "member_added": member,
                "group_name": group_name,
                "added_by": admin
            })

    except Exception as e:
        logger.error(f"Error parsing event inserts for ID {event_id}: {e}")
        return

    payload = {
        "source": "windows-security-log",
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "event_type": event_type,
        "description": description,
        "severity": severity,
        "raw_data": raw_data
    }

    client.send_event(payload)

def monitor_events():
    client = SecureOpsClient()
    
    # Try a baseline login to verify connection
    if not client.login():
        logger.warning("Could not establish initial connection to SecureOps API. Will retry when events occur.")

    log_type = "Security"
    logger.info(f"Opening Windows Event Log channel: {log_type}...")
    try:
        hand = win32evtlog.OpenEventLog(None, log_type)
    except Exception as e:
        logger.error(f"Permission Denied or Error opening Security Log: {e}")
        logger.error("=" * 60)
        logger.error("ERROR: ACCESS DENIED TO SECURITY EVENT LOGS.")
        logger.error("To read Security Logs, Windows requires running with Administrator privileges.")
        logger.error("Please run your command prompt/terminal as an Administrator and try again.")
        logger.error("=" * 60)
        sys.exit(1)

    # Establish initial checkpoint
    latest_record_number = 0
    try:
        events = win32evtlog.ReadEventLog(
            hand,
            win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
            0
        )
        if events:
            latest_record_number = events[0].RecordNumber
            logger.info(f"Baseline checkpoint established at Record Number: {latest_record_number}")
    except Exception as e:
        logger.warning(f"Could not read latest record number for checkpoint, using 0 as baseline: {e}")

    logger.info("Monitoring for new Windows Security logs in real-time...")

    while True:
        try:
            # Read FORWARDS from latest record number + 1
            events = win32evtlog.ReadEventLog(
                hand,
                win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEEK_READ,
                latest_record_number + 1
            )
            if events:
                for event in events:
                    if event.RecordNumber > latest_record_number:
                        latest_record_number = event.RecordNumber
                    process_and_forward_event(event, client)
            
            time.sleep(2)
        except Exception as e:
            # If log gets cleared or error occurs, log it and sleep
            logger.error(f"Error reading event log: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_events()
