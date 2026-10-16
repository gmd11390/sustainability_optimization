"""Configuration from environment variables. Never commit real credentials."""
import os
API_KEY = os.getenv("MERAKI_API_KEY", "")
ORG_ID = os.getenv("MERAKI_ORG_ID", "")
NETWORK_ID = os.getenv("MERAKI_NETWORK_ID", "")
SERIAL_NUMBERS = [s.strip() for s in os.getenv("MERAKI_SERIAL_NUMBERS", "").split(",") if s.strip()]
