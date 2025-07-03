#!/usr/bin/env python3
"""
Get deployment digests or logs from Corrino API
Usage: 
  python get_deployment_info.py digests <hash>
  python get_deployment_info.py logs <hash>
"""

import requests
import json
import sys
import urllib3
import argparse

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate(base_url, username, password):
    """Get authentication token"""
    session = requests.Session()
    session.verify = False
    
    login_url = f"{base_url}/login/"
    form_data = {'username': username, 'password': password}
    
    response = session.post(login_url, data=form_data)
    
    if response.status_code == 200:
        auth_data = response.json()
        if 'token' in auth_data:
            token = auth_data['token']
            session.headers.update({
                'Authorization': f"Token {token}",
                'Content-Type': 'application/json'
            })
            return session, token
    
    return None, None

def get_deployment_info(endpoint_type, deployment_hash, api_url):
    """Get deployment digests or logs"""
    
    # API credentials
    username = "dk"
    password = "iampaul1190"
    
    # Authenticate
    print(f"🔐 Authenticating with {api_url}...")
    session, token = authenticate(api_url, username, password)
    
    if not session:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated successfully")
    
    # Build endpoint URL
    if endpoint_type == "digests":
        endpoint = f"/deployment_digests/{deployment_hash}"
    elif endpoint_type == "logs":
        endpoint = f"/deployment_logs/{deployment_hash}"
    else:
        print(f"❌ Invalid endpoint type: {endpoint_type}")
        return False
    
    url = f"{api_url}{endpoint}"
    print(f"📡 Fetching from: {url}")
    
    # Make the request
    try:
        response = session.get(url)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully retrieved data!")
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                try:
                    data = response.json()
                    print("📋 JSON Response:")
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print("📋 Raw Response (invalid JSON):")
                    print(response.text)
            else:
                print("📋 Text Response:")
                print(response.text)
            
            return True
            
        elif response.status_code == 404:
            print(f"❌ Deployment hash '{deployment_hash}' not found")
            return False
        elif response.status_code == 403:
            print("❌ Access denied - check permissions")
            return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error making request: {e}")
        return False

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get deployment digests or logs from Corrino API")
    parser.add_argument("-e", "--endpoint", choices=["digests", "logs"], required=True, help="Type of endpoint to fetch")
    parser.add_argument("-d", "--deployment_hash", help="Deployment hash to fetch (if none, will fetch all deployments)")
    parser.add_argument("-a", "--api-url", required=True, help="API URL")
    return parser.parse_args()


def main():
    
    args = get_args()
    endpoint_type = args.endpoint.lower()
    deployment_hash = args.deployment_hash
    api_url = args.api_url

    
    print(f"Corrino API - Get Deployment {endpoint_type.title()}")
    print("=" * 50)
    print(f"Endpoint: {endpoint_type}")
    print(f"Hash: {deployment_hash}")
    print()
    
    success = get_deployment_info(endpoint_type, deployment_hash, api_url)
    
    if success:
        print(f"\n🎉 Successfully retrieved {endpoint_type}!")
    else:
        print(f"\n💥 Failed to retrieve {endpoint_type}!")
        sys.exit(1)

if __name__ == "__main__":
    main() 