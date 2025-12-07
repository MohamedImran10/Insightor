#!/usr/bin/env python3
"""
Firestore Database Setup Script
Creates the Firestore database and initial collections for the Insightor project
"""

import os
import sys
import logging
from datetime import datetime

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud import firestore as gcloud_firestore
except ImportError as e:
    print(f"❌ Error importing Firebase libraries: {e}")
    print("💡 Install Firebase SDK: pip install firebase-admin google-cloud-firestore")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_firestore():
    """Initialize Firestore database and create initial structure"""
    
    try:
        # Initialize Firebase Admin SDK
        logger.info("🔐 Initializing Firebase Admin SDK...")
        
        # Use service account credentials
        cred_path = "service-keys/research-agent-b7cb0-f7d0c42f295e.json"
        if not os.path.exists(cred_path):
            logger.error(f"❌ Credentials file not found: {cred_path}")
            return False
        
        cred = credentials.Certificate(cred_path)
        
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase Admin SDK initialized")
        
        # Initialize Firestore client
        logger.info("🗄️  Initializing Firestore client...")
        db = firestore.client()
        
        # Test basic connection
        logger.info("🧪 Testing Firestore connection...")
        test_doc = db.collection('_setup_test').document('test')
        test_doc.set({
            'created_at': datetime.now(),
            'status': 'setup_test',
            'project': 'insightor'
        })
        logger.info("✅ Firestore write test successful")
        
        # Create initial collections structure
        logger.info("📁 Creating initial collections...")
        
        # Create users collection with example structure
        users_col = db.collection('users')
        example_user_doc = users_col.document('_structure_example')
        example_user_doc.set({
            'created_at': datetime.now(),
            'is_example': True,
            'structure_info': 'This document shows the users collection structure'
        })
        
        # Create search_history subcollection example
        history_col = example_user_doc.collection('search_history')
        example_history = history_col.document('_structure_example')
        example_history.set({
            'query': 'example search query',
            'response': 'example response',
            'sources': [],
            'search_results': [],
            'insights': [],
            'memory_chunks': [],
            'created_at': datetime.now(),
            'is_example': True
        })
        
        # Clean up test documents
        logger.info("🧹 Cleaning up test documents...")
        test_doc.delete()
        
        logger.info("✅ Firestore database setup completed successfully!")
        logger.info("📊 Collections created:")
        logger.info("   - users/")
        logger.info("   - users/{uid}/search_history/")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firestore setup failed: {str(e)}")
        
        if "does not exist" in str(e) and "database" in str(e):
            logger.error("")
            logger.error("🔧 DATABASE CREATION REQUIRED:")
            logger.error("   1. Go to Firebase Console: https://console.firebase.google.com/project/research-agent-b7cb0")
            logger.error("   2. Navigate to 'Firestore Database'")
            logger.error("   3. Click 'Create database'")
            logger.error("   4. Choose 'Start in production mode' or 'test mode'")
            logger.error("   5. Select a location (e.g., us-central1)")
            logger.error("   6. Run this script again")
            logger.error("")
        
        return False

def check_firestore_status():
    """Check if Firestore is properly configured"""
    
    try:
        # Initialize Firebase if needed
        cred_path = "service-keys/research-agent-b7cb0-f7d0c42f295e.json"
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Try to read from users collection
        users_ref = db.collection('users').limit(1)
        docs = users_ref.stream()
        
        logger.info("✅ Firestore is working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Firestore check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Firestore Database Setup...")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        print("🔍 Checking Firestore status...")
        if check_firestore_status():
            print("✅ Firestore is ready!")
        else:
            print("❌ Firestore needs setup")
    else:
        if setup_firestore():
            print("\n🎉 Setup completed! You can now use Firestore history features.")
        else:
            print("\n❌ Setup failed. Please check the errors above and try again.")