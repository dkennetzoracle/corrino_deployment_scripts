#!/usr/bin/env python3
"""
Undeploys a deployment
Usage: python undeploy.py -a <api_url> -d <deployment_id>
"""

import argparse
import requests
import getpass
import sys
import json
import urllib3

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

def undeploy_deployment(api_url, deployment_id, username, password):
    """Undeploy a deployment"""
    session, token = authenticate(api_url, username, password)
    
    if not session:
        print("❌ Authentication failed")
        return False
    
    request_body = {
        "deployment_uuid": deployment_id
    }

    url = f"{api_url}/undeploy/"
    print(f"📡 Undeploying deployment: {url}")

    try:
        response = session.post(url, json=request_body)
        
        if response.status_code == 200:
            print("✅ Deployment undeployed successfully")
            return True
    except Exception as e:
        print(f"❌ Error undeploying deployment: {e}")
        return False

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corrino API Client")
    parser.add_argument("-a", "--api-url", type=str, help="Corrino API URL")
    parser.add_argument("-d", "--deployment-uuid", type=str, help="Deployment file to post")
    return parser.parse_args()

def main():
    # API URL - could also be made configurable if needed
    args = get_args()
    api_url = args.api_url
    deployment_uuid = args.deployment_uuid
    
    print("Corrino API Client")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Deployment UUID: {deployment_uuid}")
    print()
    
    # Get credentials from user input
    print("Please enter your credentials:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        sys.exit(1)
    
    success = undeploy_deployment(api_url, deployment_uuid, username, password)
    
    if success:
        print("\n🎉 Successfully undeployed deployment!")
    else:
        print("\n❌ Failed to undeploy deployment")

if __name__ == "__main__":
    main()