#!/usr/bin/env python3
"""
Script to check if credentials.json is properly formatted for Blogger API
"""

import json
import os

def check_credentials():
    """Check if credentials.json is properly formatted"""
    credentials_file = 'credentials.json'
    
    if not os.path.exists(credentials_file):
        print("❌ credentials.json file not found!")
        print("Please download it from Google Cloud Console and place it in the current directory.")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        print("✅ credentials.json file found")
        
        # Check if it's the right type
        if 'installed' in creds:
            print("✅ File contains 'installed' key - correct for desktop application")
            
            installed = creds['installed']
            required_keys = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            
            missing_keys = []
            for key in required_keys:
                if key not in installed:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"❌ Missing required keys: {missing_keys}")
                return False
            else:
                print("✅ All required keys present")
                return True
                
        elif 'web' in creds:
            print("❌ File contains 'web' key - this is for web applications")
            print("You need to create a 'Desktop application' credential instead")
            return False
        else:
            print("❌ File doesn't contain 'installed' or 'web' key")
            print("This doesn't appear to be a valid OAuth 2.0 credentials file")
            return False
            
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {str(e)}")
        return False

if __name__ == "__main__":
    print("Checking Blogger API credentials...")
    print("=" * 50)
    
    if check_credentials():
        print("\n✅ Credentials file looks good!")
        print("You should be able to run the Blogger authentication now.")
    else:
        print("\n❌ Credentials file needs to be fixed.")
        print("\nTo fix this:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("5. Choose 'Desktop application' as the application type")
        print("6. Download the JSON file and save as 'credentials.json'")
