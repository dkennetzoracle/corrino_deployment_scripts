#!/usr/bin/env python3
"""
List current deployments to see available hashes
Usage: python list_deployments.py
"""

import requests
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

def list_deployments():
    """List all deployments"""
    
    # API credentials
    api_url = "https://api.10-0-1-92.nip.io"
    username = "dk"
    password = "iampaul1190"
    
    # Authenticate
    print(f"🔐 Authenticating with {api_url}...")
    session, token = authenticate(api_url, username, password)
    
    if not session:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated successfully")
    
    # Get deployments
    url = f"{api_url}/deployment/"
    print(f"📡 Fetching deployments from: {url}")
    
    try:
        response = session.get(url)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            deployments = response.json()
            
            if not deployments:
                print("📭 No deployments found")
                return True
            
            print(f"📋 Found {len(deployments)} deployment(s):")
            print()
            
            for i, deployment in enumerate(deployments, 1):
                print(f"Deployment {i}:")
                print(f"     Mode: {deployment.get('mode', 'N/A')}")
                print(f"  📦 Name: {deployment.get('deployment_name', 'N/A')}")
                print(f"  🔗 Hash: {deployment.get('deployment_uuid', 'N/A')}")
                print(f"  📅 Created: {deployment.get('creation_date', 'N/A')}")
                print(f"  🔄 Status: {deployment.get('deployment_status', 'N/A')}")
                print(f"     Directive: {deployment.get('deployment_directive', 'N/A')}")
                
                # Show a few more useful fields if available
                for field in ['recipe_id', 'recipe_mode', 'recipe_node_shape']:
                    if field in deployment:
                        print(f"  🏷️  {field}: {deployment[field]}")
                
                print()
            
            # Show commands to get more info
            print("💡 To get deployment info, use:")
            for deployment in deployments:
                hash_val = deployment.get('deployment_hash')
                if hash_val:
                    print(f"  python get_deployment_info.py digests {hash_val}")
                    print(f"  python get_deployment_info.py logs {hash_val}")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error making request: {e}")
        return False

def main():
    print("Corrino API - List Deployments")
    print("=" * 40)
    
    success = list_deployments()
    
    if success:
        print("\n🎉 Successfully retrieved deployments!")
    else:
        print("\n💥 Failed to retrieve deployments!")

if __name__ == "__main__":
    main() 
