"""
Main FastAPI application
Exposes research endpoint and health checks
Phase 3: Multi-user, RAG-powered research with Qdrant + Firebase
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional
import random
import time

from fastapi import FastAPI, HTTPException, status, Depends
from firebase_admin import firestore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from app.config import settings
from app.models import (
    ResearchRequest, ResearchResponse, HealthResponse,
    ExtendedResearchResponse, UserInfo, ResearchHistoryResponse,
    ResearchHistoryItem, TopicGraphResponse
)
from app.agents.orchestrator import ResearchOrchestrator
from app.agents.embeddings import EmbeddingGenerator
from app.agents.chroma_memory import ChromaMemory
from app.agents.qdrant_memory import QdrantMemory
from app.agents.followup_agent import FollowupAgent
from app.agents.citation_extractor import CitationExtractor
from app.agents.topic_graph_agent import TopicGraphAgent
from app.auth import FirebaseAuth, initialize_firebase, get_firebase_auth
from app.auth_middleware import initialize_auth_middleware
from app.dependencies import get_current_user, get_user_id
from app.firestore_history import get_history_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
orchestrator: Optional[ResearchOrchestrator] = None
qdrant_memory: Optional[QdrantMemory] = None
followup_agent: Optional[FollowupAgent] = None
citation_extractor: Optional[CitationExtractor] = None
topic_graph_agent: Optional[TopicGraphAgent] = None
firebase_auth: Optional[FirebaseAuth] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown
    Phase 3: Initialize Qdrant, Firebase, and new agents
    """
    # Startup
    global orchestrator, qdrant_memory, followup_agent, citation_extractor, topic_graph_agent, firebase_auth
    try:
        logger.info("🚀 Initializing Phase 3 Research System...")
        
        # Initialize Auth Middleware
        logger.info("🔐 Initializing Firebase Auth Middleware...")
        initialize_auth_middleware(firebase_enabled=settings.firebase_enabled)
        logger.info("✅ Auth middleware initialized")
        
        # Initialize Orchestrator
        logger.info("📡 Initializing Research Orchestrator...")
        orchestrator = ResearchOrchestrator(
            tavily_key=settings.tavily_api_key,
            gemini_key=settings.google_api_key
        )
        logger.info("✅ Orchestrator initialized")
        
        # Initialize Qdrant Cloud (optional - can fail gracefully)
        logger.info("🔗 Initializing Qdrant Cloud Memory...")
        qdrant_memory = QdrantMemory(
            qdrant_url=settings.qdrant_url,
            qdrant_api_key=settings.qdrant_api_key,
            vector_size=384
        )
        try:
            await qdrant_memory.ensure_collections()
            logger.info("✅ Qdrant Cloud initialized")
        except Exception as e:
            logger.warning(f"⚠️  Qdrant initialization failed (will use ChromaDB only): {str(e)}")
            logger.info("💡 To enable Qdrant: start Qdrant server or configure Qdrant Cloud URL")
        
        # Initialize Firebase (optional)
        if settings.firebase_enabled:
            logger.info("🔐 Initializing Firebase Auth...")
            try:
                firebase_auth = initialize_firebase(settings.firebase_credentials_path)
                logger.info("✅ Firebase initialized")
            except Exception as e:
                logger.warning(f"⚠️  Firebase initialization failed: {str(e)}")
        
        # Initialize new agents (Phase 3 - optional)
        logger.info("🤖 Initializing Phase 3 Agents...")
        try:
            followup_agent = FollowupAgent(gemini_api_key=settings.google_api_key)
            citation_extractor = CitationExtractor()
            topic_graph_agent = TopicGraphAgent(
                chroma_memory=orchestrator.memory_agent.chroma_memory,
                embedder=orchestrator.memory_agent.embedder
            )
            logger.info("✅ All Phase 3 agents initialized")
        except Exception as e:
            logger.warning(f"⚠️  Phase 3 agent initialization failed (core features will work): {str(e)}")
        
        logger.info("✅✅✅ Phase 3 System Ready!")
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Insightor - AI Research Assistant",
    description="Phase-1: Search Agent → Reader Agent → Gemini LLM Pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Insightor - AI Research Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/verify", tags=["Auth"])
async def verify_token(user: dict = Depends(get_current_user)):
    """
    Verify Firebase ID token
    
    Args:
        user: Current authenticated user
    
    Returns:
        User information (uid, email, name, etc.)
    """
    return {
        "status": "authenticated",
        "uid": user.get("uid"),
        "email": user.get("email"),
        "name": user.get("name"),
        "email_verified": user.get("email_verified"),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/auth/logout", tags=["Auth"])
async def logout(user: dict = Depends(get_current_user)):
    """
    Logout endpoint (client should clear token from localStorage)
    
    Args:
        user: Current authenticated user
    
    Returns:
        Logout confirmation
    """
    logger.info(f"👋 User {user.get('uid')} logged out")
    return {
        "status": "logged_out",
        "message": "Please clear the authentication token from your client"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Verifies that all agents are properly initialized
    """
    try:
        agents_status = await orchestrator.validate_pipeline()
        
        return HealthResponse(
            status="healthy" if agents_status.get("pipeline_ready") else "degraded",
            timestamp=datetime.now().isoformat(),
            agents_ready=agents_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not available"
        )


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
async def research(
    request: ResearchRequest,
    user: dict = Depends(get_current_user)
):
    """
    Main research endpoint (REQUIRES AUTHENTICATION)
    
    Executes the full pipeline:
    1. Search Agent → Tavily Search API
    2. Reader Agent → Content fetching and cleaning
    3. Gemini Summarizer → LLM-based summarization
    
    Args:
        request: ResearchRequest with query field
        user: Authenticated user from Firebase token
        
    Returns:
        ResearchResponse with results and summary
        
    Raises:
        HTTPException: If research fails or not authenticated
    """
    user_id = user.get("uid")
    user_email = user.get("email")
    logger.info(f"📥 Research request from {user_email} ({user_id[:8]}...): {request.query}")
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        logger.info(f"📥 Received research request: {request.query}")
        
        # Execute research pipeline
        result = await orchestrator.execute_research(request.query)
        
        if result.get("status") == "error":
            logger.error(f"Research failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Research failed")
            )
        
        logger.info(f"✅ Research completed successfully")
        
        # Auto-save to history (fire and forget)
        try:
            history_manager = get_history_manager()
            if history_manager:
                # Extract relevant data from result
                search_results = result.get("search_results", [])
                response_text = result.get("final_summary", "")
                insights = result.get("top_insights", [])
                memory_chunks = result.get("relevant_memory_chunks", [])
                
                # Save asynchronously in background
                import asyncio
                asyncio.create_task(history_manager.save_search_history(
                    user_id=user_id,
                    query=request.query,
                    response=response_text,
                    sources=search_results,  # Use search_results as sources
                    search_results=search_results,
                    insights=insights,
                    memory_chunks=memory_chunks
                ))
                logger.info(f"💾 Queued history save for user {user_id[:8]}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to queue history save: {str(e)}")
            # Don't fail the request if history save fails
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in research endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research failed: {str(e)}"
        )


@app.get("/status", tags=["Health"])
async def get_status():
    """
    Get application status
    """
    return {
        "application": "Insightor AI Research Assistant",
        "phase": "Phase-1: Search → Reader → Gemini",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "api_version": "v1",
        "endpoints": {
            "research": "POST /research",
            "health": "GET /health",
            "docs": "GET /docs",
            "memory_debug": "GET /memory/debug"
        }
    }


@app.get("/memory/debug", tags=["Debug"])
async def memory_debug():
    """
    Memory Debug Mode endpoint
    
    Returns comprehensive debugging information about ChromaDB memory:
    - Collection statistics
    - Sample research chunks
    - Sample topic memory
    - Retrieval diagnostics
    
    Useful for monitoring memory growth and validating embedding/retrieval behavior.
    """
    try:
        logger.info("🔍 Memory Debug endpoint called")
        
        # Get embedder and memory instances
        embedder = EmbeddingGenerator()
        chroma_memory = ChromaMemory()
        
        # === 1. CHROMA STATS ===
        stats = chroma_memory.get_collection_stats()
        
        debug_response = {
            "stats": {
                "research_chunks_count": stats.get("research_chunks", 0),
                "topic_memory_count": stats.get("topic_memory", 0),
                "total_entries": stats.get("total_entries", 0),
                "embedding_dimension": embedder.embedding_dim,
                "embedding_model": embedder.model_name,
                "db_path": stats.get("db_path", "N/A"),
            },
            "sample_research_chunk": None,
            "sample_topic_memory": None,
            "retrieval_test": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # === 2. SAMPLE RESEARCH CHUNK ===
        try:
            chunk_count = chroma_memory.research_chunks.count()
            if chunk_count > 0:
                # Get all data and pick a random one
                all_chunks = chroma_memory.research_chunks.get()
                
                if all_chunks.get("ids") and len(all_chunks["ids"]) > 0:
                    # Pick random index
                    idx = random.randint(0, len(all_chunks["ids"]) - 1)
                    chunk_id = all_chunks["ids"][idx]
                    chunk_text = all_chunks["documents"][idx]
                    chunk_metadata = all_chunks["metadatas"][idx] if all_chunks.get("metadatas") else {}
                    
                    # Cap text at 500 chars
                    chunk_text_preview = chunk_text[:500] if chunk_text else ""
                    
                    debug_response["sample_research_chunk"] = {
                        "id": chunk_id,
                        "text_preview": chunk_text_preview,
                        "full_length": len(chunk_text) if chunk_text else 0,
                        "metadata": chunk_metadata
                    }
                    logger.info(f"✅ Sample research chunk retrieved (id={chunk_id}, len={len(chunk_text)})")
        except Exception as e:
            logger.warning(f"⚠️  Could not retrieve sample research chunk: {str(e)}")
            debug_response["sample_research_chunk"] = {"error": str(e)}
        
        # === 3. SAMPLE TOPIC MEMORY ===
        try:
            memory_count = chroma_memory.topic_memory.count()
            if memory_count > 0:
                # Get all topic memory entries
                all_memory = chroma_memory.topic_memory.get()
                
                if all_memory.get("ids") and len(all_memory["ids"]) > 0:
                    # Pick random index
                    idx = random.randint(0, len(all_memory["ids"]) - 1)
                    memory_id = all_memory["ids"][idx]
                    memory_text = all_memory["documents"][idx]
                    memory_metadata = all_memory["metadatas"][idx] if all_memory.get("metadatas") else {}
                    
                    # Cap text at 500 chars
                    memory_text_preview = memory_text[:500] if memory_text else ""
                    
                    debug_response["sample_topic_memory"] = {
                        "id": memory_id,
                        "text_preview": memory_text_preview,
                        "full_length": len(memory_text) if memory_text else 0,
                        "metadata": memory_metadata
                    }
                    logger.info(f"✅ Sample topic memory retrieved (id={memory_id}, len={len(memory_text)})")
        except Exception as e:
            logger.warning(f"⚠️  Could not retrieve sample topic memory: {str(e)}")
            debug_response["sample_topic_memory"] = {"error": str(e)}
        
        # === 4. RETRIEVAL DIAGNOSTICS ===
        try:
            test_query = "test"
            logger.info(f"🔎 Running retrieval diagnostics with test query: '{test_query}'")
            
            # Embed the test query
            test_embedding = embedder.encode(test_query)
            logger.info(f"✅ Test query embedded (dim={len(test_embedding)})")
            
            # Retrieve top-3 from research_chunks
            retrieval_results = chroma_memory.retrieve_similar_chunks(
                query_embedding=test_embedding,
                n_results=3,
                query_text=None
            )
            
            # Format retrieval results
            formatted_chunks = []
            if retrieval_results.get("chunks"):
                for chunk_info in retrieval_results["chunks"]:
                    formatted_chunks.append({
                        "id": chunk_info.get("metadata", {}).get("id", "N/A"),
                        "text_preview": chunk_info.get("content", "")[:300],  # 300 char preview
                        "full_length": len(chunk_info.get("content", "")),
                        "similarity_score": round(chunk_info.get("similarity", 0), 4),
                        "metadata": chunk_info.get("metadata", {})
                    })
            
            debug_response["retrieval_test"] = {
                "query": test_query,
                "test_embedding_dim": len(test_embedding),
                "results_count": len(formatted_chunks),
                "top_results": formatted_chunks
            }
            
            logger.info(f"✅ Retrieval diagnostics complete ({len(formatted_chunks)} results)")
            
        except Exception as e:
            logger.error(f"❌ Retrieval diagnostics failed: {str(e)}")
            debug_response["retrieval_test"] = {"error": str(e)}
        
        logger.info("✅ Memory debug endpoint completed successfully")
        return debug_response
        
    except Exception as e:
        logger.error(f"❌ Memory debug endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory debug failed: {str(e)}"
        )


@app.get("/research/history", tags=["Research"])
async def research_history(
    user_id: str = Depends(lambda creds: creds if settings.firebase_enabled else "default_user") if settings.firebase_enabled else "default_user",
    limit: int = 20,
    offset: int = 0
):
    """
    Get research history for authenticated user
    
    Args:
        user_id: User ID from Firebase token (if enabled)
        limit: Max results per page
        offset: Pagination offset
    
    Returns:
        List of past research summaries
    """
    try:
        if not qdrant_memory:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Qdrant memory not initialized"
            )
        
        logger.info(f"📜 Fetching research history for user {user_id[:8]}...")
        history_data = await qdrant_memory.retrieve_history(user_id, limit, offset)
        
        history_items = [
            ResearchHistoryItem(
                id=item.get("id"),
                query=item.get("query"),
                timestamp=item.get("timestamp"),
                summary_preview=item.get("text_preview"),
                insights_count=item.get("insights_count", 0),
                sources_count=item.get("sources_count", 0)
            )
            for item in history_data.get("history", [])
        ]
        
        return ResearchHistoryResponse(
            history=history_items,
            total_count=history_data.get("count", 0),
            page=offset // limit if limit > 0 else 0,
            limit=limit
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@app.delete("/research/{summary_id}", tags=["Research"])
async def delete_research(
    summary_id: str,
    user_id: str = Depends(lambda creds: creds if settings.firebase_enabled else "default_user") if settings.firebase_enabled else "default_user"
):
    """
    Delete a specific research summary
    
    Args:
        summary_id: ID of summary to delete
        user_id: User ID for authorization
    
    Returns:
        Success status
    """
    try:
        if not qdrant_memory:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Qdrant memory not initialized"
            )
        
        logger.info(f"🗑️  Deleting summary {summary_id[:8]}... for user {user_id[:8]}...")
        success = await qdrant_memory.delete_summary(user_id, summary_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found or unauthorized"
            )
        
        return {"status": "deleted", "id": summary_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete summary: {str(e)}"
        )


@app.delete("/research/all", tags=["Research"])
async def delete_all_research(
    user_id: str = Depends(lambda creds: creds if settings.firebase_enabled else "default_user") if settings.firebase_enabled else "default_user"
):
    """
    Delete ALL research data for user
    
    Args:
        user_id: User ID
    
    Returns:
        Success status
    """
    try:
        if not qdrant_memory:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Qdrant memory not initialized"
            )
        
        logger.info(f"⚠️  DELETING ALL DATA for user {user_id[:8]}...")
        success = await qdrant_memory.delete_user_data(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete all data"
            )
        
        return {"status": "deleted", "message": "All user data cleared"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete all research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data: {str(e)}"
        )


@app.get("/topics/graph", tags=["Topics"])
async def get_topic_graph(
    user_id: str = Depends(lambda creds: creds if settings.firebase_enabled else "default_user") if settings.firebase_enabled else "default_user",
    limit: int = 50
):
    """
    Get user's topic knowledge graph
    
    Args:
        user_id: User ID
        limit: Max topics to return
    
    Returns:
        Topic graph with nodes and edges
    """
    try:
        if not topic_graph_agent:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Topic graph not initialized"
            )
        
        logger.info(f"📊 Fetching topic graph for user {user_id[:8]}...")
        graph_data = await topic_graph_agent.get_topic_graph(user_id, limit)
        
        return TopicGraphResponse(
            nodes=graph_data.get("nodes", []),
            edges=graph_data.get("edges", []),
            node_count=graph_data.get("node_count", 0),
            edge_count=graph_data.get("edge_count", 0)
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch topic graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch topic graph: {str(e)}"
        )


# ============================================
# SEARCH HISTORY ENDPOINTS
# ============================================

@app.post("/history/save", tags=["History"])
async def save_search_history(
    query: str,
    response: str,
    sources: list = None,
    search_results: list = None,
    insights: list = None,
    memory_chunks: list = None,
    user: dict = Depends(get_current_user)
):
    """
    Save a search query and response to user's history
    
    Args:
        query: The search query
        response: The research response/summary
        sources: List of source documents used
        search_results: Search results from Tavily
        insights: Extracted insights
        memory_chunks: Related memory chunks
        user: Authenticated user
        
    Returns:
        Status confirmation
    """
    user_id = user.get("uid")
    logger.info(f"💾 Saving search history for user {user_id[:8]}: {query[:50]}...")
    
    try:
        history_manager = get_history_manager()
        if not history_manager:
            logger.warning("⚠️  History manager not available")
            return {
                "status": "warning",
                "message": "History manager not available",
                "saved": False
            }
        
        success = await history_manager.save_search_history(
            user_id=user_id,
            query=query,
            response=response,
            sources=sources or [],
            search_results=search_results,
            insights=insights,
            memory_chunks=memory_chunks
        )
        
        if success:
            logger.info(f"✅ History saved for user {user_id[:8]}")
            return {
                "status": "success",
                "message": "History saved successfully",
                "saved": True
            }
        else:
            logger.warning(f"⚠️  Failed to save history for user {user_id[:8]}")
            return {
                "status": "error",
                "message": "Failed to save history",
                "saved": False
            }
    
    except Exception as e:
        logger.error(f"❌ Error saving history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save history: {str(e)}"
        )


@app.get("/history/{user_id}", tags=["History"])
async def get_search_history(
    user_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get search history for a user
    
    Args:
        user_id: User ID to fetch history for
        limit: Maximum number of entries to return
        current_user: Authenticated user (must match user_id for security)
        
    Returns:
        List of history entries
    """
    # Security: Users can only view their own history
    current_user_id = current_user.get("uid")
    if current_user_id != user_id:
        logger.warning(f"❌ Unauthorized history access attempt: {current_user_id[:8]} tried to access {user_id[:8]}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own search history"
        )
    
    logger.info(f"📖 Fetching search history for user {user_id[:8]}")
    
    try:
        history_manager = get_history_manager()
        if not history_manager:
            logger.warning("⚠️  History manager not available")
            return {
                "status": "warning",
                "message": "History manager not available",
                "history": []
            }
        
        history = await history_manager.get_search_history(user_id, limit)
        
        logger.info(f"✅ Retrieved {len(history)} history entries for user {user_id[:8]}")
        return {
            "status": "success",
            "user_id": user_id,
            "count": len(history),
            "history": history
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@app.post("/setup/firestore", tags=["Setup"])
async def setup_firestore():
    """
    Initialize Firestore database manually
    This endpoint can be called to test and initialize Firestore
    """
    try:
        history_manager = get_history_manager()
        if not history_manager:
            return {
                "status": "error",
                "message": "History manager not available - check Firebase credentials"
            }
        
        if not history_manager.db:
            return {
                "status": "error", 
                "message": "Firestore database not initialized. Please create database in Firebase Console first.",
                "instructions": [
                    "1. Go to: https://console.firebase.google.com/project/research-agent-b7cb0/firestore",
                    "2. Click 'Create database'",
                    "3. Choose 'Start in test mode'", 
                    "4. Select a location (us-central1 recommended)",
                    "5. Try this endpoint again"
                ]
            }
        
        # Test database by creating a sample document
        test_doc = history_manager.db.collection('_setup').document('test')
        test_doc.set({
            'setup_time': firestore.SERVER_TIMESTAMP,
            'message': 'Firestore successfully initialized!'
        })
        
        # Clean up test document
        test_doc.delete()
        
        logger.info("✅ Firestore database setup successful")
        return {
            "status": "success",
            "message": "Firestore database is working correctly!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Firestore setup failed: {e}")
        error_msg = str(e)
        
        if "does not exist" in error_msg.lower():
            return {
                "status": "error",
                "message": "Firestore database does not exist",
                "error": error_msg,
                "instructions": [
                    "Please create the Firestore database manually:",
                    "1. Go to: https://console.firebase.google.com/project/research-agent-b7cb0/firestore", 
                    "2. Click 'Create database'",
                    "3. Choose 'Start in test mode'",
                    "4. Select a location (us-central1 recommended)"
                ]
            }
        
        return {
            "status": "error",
            "message": f"Firestore setup failed: {error_msg}",
            "error": error_msg
        }


@app.delete("/history/{user_id}/{entry_id}", tags=["History"])
async def delete_history_entry(
    user_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific history entry
    
    Args:
        user_id: User ID
        entry_id: History entry ID to delete
        current_user: Authenticated user (must match user_id)
        
    Returns:
        Deletion status
    """
    # Security: Users can only delete their own history
    current_user_id = current_user.get("uid")
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own history"
        )
    
    logger.info(f"🗑️  Deleting history entry {entry_id} for user {user_id[:8]}")
    
    try:
        history_manager = get_history_manager()
        if not history_manager:
            return {
                "status": "warning",
                "message": "History manager not available",
                "deleted": False
            }
        
        success = await history_manager.delete_history_entry(user_id, entry_id)
        
        if success:
            logger.info(f"✅ Deleted history entry {entry_id}")
            return {
                "status": "success",
                "message": "History entry deleted",
                "deleted": True
            }
        else:
            return {
                "status": "error",
                "message": "Failed to delete history entry",
                "deleted": False
            }
    
    except Exception as e:
        logger.error(f"❌ Error deleting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete history: {str(e)}"
        )


@app.get("/system/status", tags=["System"])
async def system_status():
    """
    Get system status and analytics
    
    Returns:
        System stats including memory usage, runtime, etc.
    """
    try:
        stats = {}
        
        if qdrant_memory:
            qdrant_stats = await qdrant_memory.get_stats()
            stats["qdrant"] = qdrant_stats
        
        stats["system"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0-phase3",
            "components": {
                "orchestrator": orchestrator is not None,
                "qdrant_memory": qdrant_memory is not None,
                "followup_agent": followup_agent is not None,
                "citation_extractor": citation_extractor is not None,
                "topic_graph_agent": topic_graph_agent is not None,
                "firebase_auth": firebase_auth is not None and settings.firebase_enabled
            }
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level="info"
    )
