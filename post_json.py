#!/usr/bin/env python3
"""
Simple utility to post JSON files to Corrino API
Usage: python post_json.py <json_file>
"""

import requests
import json
import sys
import urllib3
import os

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

def post_json_file(json_file_path):
    """Post JSON file to deployment endpoint"""
    
    # API credentials
    api_url = "https://api.10-0-1-104.nip.io"
    username = "dk"
    password = "iampaul1190"
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return False
    
    # Read and parse JSON file
    try:
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False
    
    # Authenticate
    print(f"🔐 Authenticating with {api_url}...")
    session, token = authenticate(api_url, username, password)
    
    if not session:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated successfully")
    print(f"📤 Posting {json_file_path} to /deployment endpoint...")
    
    # Post the data - try both with and without trailing slash
    endpoints_to_try = ["/deployment/", "/deployment"]
    
    for endpoint in endpoints_to_try:
        try:
            print(f"📤 Trying endpoint: {endpoint}")
            response = session.post(f"{api_url}{endpoint}", json=json_data, allow_redirects=True)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"🔗 Final URL: {response.url}")
            print(f"📋 Response: {response.text}")
            
            if response.status_code in [200, 201, 202]:
                print("✅ Successfully posted JSON data!")
                
                # Try to display response
                try:
                    if response.text and len(response.text) > 2:
                        response_data = response.json()
                        print("📋 Response:")
                        print(json.dumps(response_data, indent=2))
                    else:
                        print("📋 API returned empty/minimal response (this is normal)")
                except:
                    print(f"📋 Response text: {response.text}")
                
                return True
            elif response.status_code == 301:
                print(f"⚠️ Got redirect (301) from {endpoint}, trying next...")
                continue
            else:
                print(f"❌ Failed to post data to {endpoint}")
                print(f"📋 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error posting to {endpoint}: {e}")
            continue
    
    print("❌ Failed to post to any endpoint")
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python post_json.py <json_file>")
        print("Example: python post_json.py sample_deployment.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    print("Corrino API JSON Poster")
    print("=" * 30)
    
    success = post_json_file(json_file)
    
    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n💥 Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 