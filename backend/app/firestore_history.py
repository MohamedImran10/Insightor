"""
Firestore integration for storing user search history
Note: Firestore requires billing to be enabled. If billing is not enabled,
history saving will be disabled but the app will continue to work.
"""
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

# Database name - use your custom database name
FIRESTORE_DATABASE = "insightordb"

# Flag to enable/disable Firestore history (set to false if billing is not enabled)
FIRESTORE_ENABLED = os.getenv('FIRESTORE_ENABLED', 'false').lower() == 'true'

class FirestoreHistoryManager:
    """Manages user search history in Firestore"""
    
    def __init__(self):
        # If Firestore is disabled, skip initialization
        if not FIRESTORE_ENABLED:
            logger.info("ℹ️ Firestore history is disabled (FIRESTORE_ENABLED=false)")
            self.db = None
            return
            
        try:
            # Initialize Firestore client with specific database
            # Get the default app credentials
            app = firebase_admin.get_app()
            
            # Create Firestore client with the named database
            self.db = Client(
                project=app.project_id,
                credentials=app.credential.get_credential(),
                database=FIRESTORE_DATABASE
            )
            logger.info(f"✅ Firestore client initialized with database: {FIRESTORE_DATABASE}")
            
            # Test connection and create database if needed
            self._test_connection()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firestore: {e}")
            logger.warning(f"⚠️  Firestore database '{FIRESTORE_DATABASE}' may not exist. Please verify in Firebase Console:")
            logger.warning("   https://console.firebase.google.com/project/research-agent-b7cb0/firestore")
            self.db = None
    
    def _test_connection(self):
        """Test Firestore connection and create initial structure if needed"""
        try:
            # Try to create a test collection to verify database exists
            test_doc = self.db.collection('_test').document('connection')
            test_doc.set({'created': datetime.now(), 'status': 'active'})
            logger.info("✅ Firestore database connection verified")
            
            # Create initial collections structure
            self._initialize_collections()
            
            # Clean up test document
            test_doc.delete()
            
        except Exception as e:
            # Silently disable Firestore if billing not enabled or database doesn't exist
            logger.info("ℹ️ Firestore history disabled (billing may not be enabled)")
            self.db = None
    
    def _initialize_collections(self):
        """Initialize basic collection structure"""
        try:
            # Create a sample user document to initialize the structure
            sample_doc = self.db.collection('users').document('_sample').collection('search_history').document('_init')
            sample_doc.set({
                'query': 'Welcome to Insightor!',
                'response': 'This is a sample search history entry.',
                'sources': [],
                'timestamp': datetime.utcnow(),
                'created_at': firestore.SERVER_TIMESTAMP,
                'is_sample': True
            })
            logger.info("✅ Initialized Firestore collections structure")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize collections: {e}")
            pass
    
    async def save_search_history(
        self, 
        user_id: str, 
        query: str, 
        response: str, 
        sources: List[Dict[str, Any]],
        search_results: Optional[List[Dict]] = None,
        insights: Optional[List[str]] = None,
        memory_chunks: Optional[List[Dict]] = None
    ) -> bool:
        """
        Save a search query and response to Firestore
        
        Structure:
        users/{uid}/search_history/{entry_id}
        """
        if not self.db or not user_id:
            logger.warning(f"⚠️ Cannot save history: db={bool(self.db)}, user_id={user_id}")
            return False
        
        try:
            # Create history entry
            history_entry = {
                "query": query,
                "response": response,
                "sources": sources,
                "search_results": search_results or [],
                "insights": insights or [],
                "memory_chunks": memory_chunks or [],
                "timestamp": datetime.utcnow(),
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            # Save to Firestore
            user_history_ref = self.db.collection("users").document(user_id).collection("search_history")
            doc_ref = user_history_ref.add(history_entry)
            
            logger.info(f"✅ Saved search history for user {user_id[:8]}")
            return True
            
        except Exception as e:
            # Silent fail - don't log errors to avoid confusion when billing is not enabled
            logger.debug(f"History save skipped: {e}")
            return False
    
    async def get_search_history(
        self, 
        user_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's search history from Firestore
        
        Returns entries in reverse chronological order
        """
        if not self.db or not user_id:
            logger.warning(f"⚠️ Cannot retrieve history: db={bool(self.db)}, user_id={user_id}")
            return []
        
        try:
            # Query history collection, ordered by timestamp descending
            user_history_ref = self.db.collection("users").document(user_id).collection("search_history")
            docs = user_history_ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            history = []
            for doc in docs:
                entry = doc.to_dict()
                entry["id"] = doc.id  # Include document ID
                history.append(entry)
            
            logger.info(f"✅ Retrieved {len(history)} history entries for user {user_id[:8]}")
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve search history: {e}")
            return []
    
    async def delete_history_entry(
        self, 
        user_id: str, 
        entry_id: str
    ) -> bool:
        """Delete a specific history entry"""
        if not self.db or not user_id or not entry_id:
            return False
        
        try:
            self.db.collection("users").document(user_id).collection("search_history").document(entry_id).delete()
            logger.info(f"✅ Deleted history entry {entry_id} for user {user_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete history entry: {e}")
            return False
    
    async def clear_all_history(self, user_id: str) -> bool:
        """Clear all history for a user"""
        if not self.db or not user_id:
            return False
        
        try:
            user_history_ref = self.db.collection("users").document(user_id).collection("search_history")
            docs = user_history_ref.stream()
            
            for doc in docs:
                doc.reference.delete()
            
            logger.info(f"✅ Cleared all history for user {user_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear history: {e}")
            return False


# Global instance
history_manager: Optional[FirestoreHistoryManager] = None

def get_history_manager() -> Optional[FirestoreHistoryManager]:
    """Get the global history manager instance"""
    global history_manager
    if history_manager is None:
        history_manager = FirestoreHistoryManager()
    return history_manager
