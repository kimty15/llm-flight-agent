import sqlite3
import json
import pickle
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from logger import Logger

# Initialize logger and embedding model
logger = Logger().get_logger()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class DatabaseManager:
    def __init__(self, db_path: str = 'chat_sessions.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                messages TEXT,
                message_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Question-Answer history table with embeddings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                embedding BLOB,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT messages, message_type FROM chat_sessions WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            messages_json, message_type = result
            return {
                "messages": json.loads(messages_json) if messages_json else [],
                "message_type": message_type
            }
        return None
    
    def save_session_state(self, session_id: str, state: Dict[str, Any]):
        """Save session state to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        messages_json = json.dumps([{"role": msg.type, "content": msg.content} for msg in state["messages"]])
        
        cursor.execute('''
            INSERT OR REPLACE INTO chat_sessions (session_id, messages, message_type, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, messages_json, state.get("message_type")))
        
        conn.commit()
        conn.close()
    
    def save_qa_to_history(self, question: str, answer: str, session_id: str):
        """Save question-answer pair with embedding to database"""
        try:
            # Generate embedding for the question
            embedding = embedding_model.encode(question)
            embedding_blob = pickle.dumps(embedding)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO qa_history (question, answer, embedding, session_id)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, embedding_blob, session_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved Q&A to history for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving Q&A to history: {str(e)}")
    
    def find_similar_questions(self, question: str, similarity_threshold: float = 0.7, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """Find similar questions in the database using cosine similarity"""
        try:
            # Generate embedding for input question
            question_embedding = embedding_model.encode(question)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all Q&A pairs with embeddings
            cursor.execute('SELECT question, answer, embedding FROM qa_history')
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return []
            
            similar_qa = []
            
            for stored_question, stored_answer, embedding_blob in results:
                try:
                    # Deserialize stored embedding
                    stored_embedding = pickle.loads(embedding_blob)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(question_embedding, stored_embedding) / (
                        np.linalg.norm(question_embedding) * np.linalg.norm(stored_embedding)
                    )
                    
                    if similarity >= similarity_threshold:
                        similar_qa.append((stored_question, stored_answer, similarity))
                        
                except Exception as e:
                    logger.warning(f"Error processing stored embedding: {str(e)}")
                    continue
            
            # Sort by similarity score (descending) and return top_k
            similar_qa.sort(key=lambda x: x[2], reverse=True)
            return similar_qa[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar questions: {str(e)}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_sessions WHERE session_id = ?', (session_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def get_qa_history_stats(self) -> Dict[str, Any]:
        """Get statistics about Q&A history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM qa_history')
            total_qa = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT session_id) FROM qa_history')
            unique_sessions = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM chat_sessions')
            total_sessions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_qa_pairs": total_qa,
                "unique_sessions_with_qa": unique_sessions,
                "total_sessions": total_sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting Q&A stats: {str(e)}")
            return {}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up sessions older than specified days"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM chat_sessions 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days_old,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {str(e)}")
            return 0 