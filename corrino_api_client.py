#!/usr/bin/env python3
"""
Corrino API Client - proper authentication flow
"""

import argparse
import requests
import json
import sys
import urllib3
import getpass

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CorrinoAPIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
        
        # Set common headers
        self.session.headers.update({
            'User-Agent': 'Corrino-API-Client/1.0',
        })
    
    def login(self):
        """
        Login to get authentication token using form data
        """
        login_url = f"{self.base_url}/login/"
        
        # Use form data as specified in the documentation
        form_data = {
            'username': self.username,
            'password': self.password
        }
        
        print(f"Logging in to {login_url}")
        
        try:
            response = self.session.post(login_url, data=form_data)
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    auth_data = response.json()
                    if 'token' in auth_data:
                        self.token = auth_data['token']
                        
                        # Update session headers with the token
                        self.session.headers.update({
                            'Authorization': f"Token {self.token}",
                            'Content-Type': 'application/json'
                        })
                        
                        print("✅ Successfully authenticated!")
                        print(f"Token: {self.token[:20]}...")
                        
                        if 'is_new' in auth_data:
                            print(f"Is new user: {auth_data['is_new']}")
                        
                        return True
                    else:
                        print("❌ No token in response")
                        print(f"Response: {auth_data}")
                        return False
                        
                except json.JSONDecodeError:
                    print("❌ Invalid JSON response")
                    print(f"Response: {response.text}")
                    return False
            else:
                print(f"❌ Login failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_api_access(self):
        """
        Test API access with a simple GET request
        """
        test_endpoints = ["/oci_shapes/", "/deployment/", "/"]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url)
                print(f"GET {endpoint}: Status {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} is accessible")
                    print(f"Response: {response.text}")
                    if 'json' in response.headers.get('content-type', '').lower():
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                print(f"   Returns list with {len(data)} items")
                            elif isinstance(data, dict):
                                print(f"   Returns dict with keys: {list(data.keys())}")
                        except:
                            pass
                elif response.status_code == 403:
                    print(f"🔒 {endpoint} requires permission")
                elif response.status_code == 404:
                    print(f"❌ {endpoint} not found")
                else:
                    print(f"⚠️  {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                print(f"💥 Error testing {endpoint}: {e}")
    
    def post_deployment(self, json_data):
        """
        Post JSON data to the deployment endpoint
        """
        # Try both with and without trailing slash
        endpoints_to_try = ["/deployment/", "/deployment"]
        
        for endpoint in endpoints_to_try:
            url = f"{self.base_url}{endpoint}"
            
            print(f"\nPosting to: {url}")
            print(f"Data: {json.dumps(json_data, indent=2)}")
            
            try:
                response = self.session.post(url, json=json_data, allow_redirects=True)
                
                print(f"Response Status: {response.status_code}")
                print(f"Final URL: {response.url}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if response.status_code in [200, 201, 202]:
                    print("✅ Successfully posted deployment!")
                    try:
                        return response.json()
                    except:
                        return response.text
                elif response.status_code == 301:
                    print(f"⚠️ Got redirect (301) from {endpoint}, trying next endpoint...")
                    continue
                else:
                    print(f"❌ Failed to post deployment. Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error posting to {endpoint}: {e}")
                continue
        
        print("❌ Failed to post to any endpoint")
        return None

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corrino API Client")
    parser.add_argument("-a", "--api-url", type=str, required=True, help="Corrino API URL")
    parser.add_argument("-d", "--deployment-file", type=str, required=True, help="Deployment file to post")
    return parser.parse_args()

def main():
    # API URL - could also be made configurable if needed
    args = get_args()
    api_url = args.api_url
    deployment_file = args.deployment_file
    
    print("Corrino API Client")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print()
    
    # Get credentials from user input
    print("Please enter your credentials:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        sys.exit(1)
    
    print(f"Username: {username}")
    print()
    
    # Create client and login
    client = CorrinoAPIClient(api_url, username, password)
    
    if not client.login():
        print("❌ Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    # Test API access
    print("\nTesting API endpoints...")
    client.test_api_access()
    
    # Prepare deployment data
    with open(deployment_file, 'r') as f:
        deployment_data = json.load(f)

    
    print("\n" + "=" * 50)
    print("Deployment Data:")
    print(json.dumps(deployment_data, indent=2))
    print()
    
    # Ask user if they want to proceed
    proceed = input("Proceed with posting this deployment? (y/n): ").strip().lower()
    
    if proceed == 'y':
        result = client.post_deployment(deployment_data)
        
        if result:
            print("\n✅ Deployment posted successfully!")
            print("Response:")
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))
            else:
                print(result)
        else:
            print("\n❌ Failed to post deployment")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main() 