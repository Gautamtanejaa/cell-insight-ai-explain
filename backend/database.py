import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    analysis_id: str
    cell_counts: Dict
    diseases: List[Dict]
    abnormalities: List[str]
    confidence_scores: Dict
    image_path: str
    timestamp: str
    explanation: Optional[str] = None

class Database:
    """SQLite database for storing analysis results"""
    
    def __init__(self, db_path: str = "bloodcell_analysis.db"):
        self.db_path = db_path
        self.connection = None
    
    async def init_db(self):
        """Initialize database and create tables"""
        try:
            # Create database directory if it doesn't exist
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            
            logger.info(f"Database initialized successfully: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        
        create_analysis_table = """
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT UNIQUE NOT NULL,
            cell_counts TEXT NOT NULL,
            diseases TEXT NOT NULL,
            abnormalities TEXT NOT NULL,
            confidence_scores TEXT NOT NULL,
            image_path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            explanation TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        create_follow_up_table = """
        CREATE TABLE IF NOT EXISTS follow_up_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis_results (analysis_id)
        )
        """
        
        create_user_sessions_table = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            analysis_ids TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor = self.connection.cursor()
        cursor.execute(create_analysis_table)
        cursor.execute(create_follow_up_table)
        cursor.execute(create_user_sessions_table)
        self.connection.commit()
    
    async def save_analysis_result(self, result: AnalysisResult) -> bool:
        """Save analysis result to database"""
        try:
            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT OR REPLACE INTO analysis_results 
            (analysis_id, cell_counts, diseases, abnormalities, confidence_scores, image_path, timestamp, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, (
                result.analysis_id,
                json.dumps(result.cell_counts),
                json.dumps(result.diseases),
                json.dumps(result.abnormalities),
                json.dumps(result.confidence_scores),
                result.image_path,
                result.timestamp,
                result.explanation
            ))
            
            self.connection.commit()
            logger.info(f"Analysis result saved: {result.analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving analysis result: {str(e)}")
            return False
    
    async def get_analysis_result(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis result by ID"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT * FROM analysis_results WHERE analysis_id = ?
            """
            
            cursor.execute(query, (analysis_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'analysis_id': row['analysis_id'],
                    'cell_counts': json.loads(row['cell_counts']),
                    'diseases': json.loads(row['diseases']),
                    'abnormalities': json.loads(row['abnormalities']),
                    'confidence_scores': json.loads(row['confidence_scores']),
                    'image_path': row['image_path'],
                    'timestamp': row['timestamp'],
                    'explanation': row['explanation'],
                    'created_at': row['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting analysis result: {str(e)}")
            return None
    
    async def update_analysis_explanation(self, analysis_id: str, explanation: str) -> bool:
        """Update analysis with medical explanation"""
        try:
            cursor = self.connection.cursor()
            
            update_query = """
            UPDATE analysis_results SET explanation = ? WHERE analysis_id = ?
            """
            
            cursor.execute(update_query, (explanation, analysis_id))
            self.connection.commit()
            
            logger.info(f"Explanation updated for analysis: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating explanation: {str(e)}")
            return False
    
    async def save_follow_up_question(self, analysis_id: str, question: str, answer: str) -> bool:
        """Save follow-up question and answer"""
        try:
            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT INTO follow_up_questions (analysis_id, question, answer)
            VALUES (?, ?, ?)
            """
            
            cursor.execute(insert_query, (analysis_id, question, answer))
            self.connection.commit()
            
            logger.info(f"Follow-up question saved for analysis: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving follow-up question: {str(e)}")
            return False
    
    async def get_follow_up_questions(self, analysis_id: str) -> List[Dict]:
        """Get all follow-up questions for an analysis"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT question, answer, timestamp FROM follow_up_questions 
            WHERE analysis_id = ? ORDER BY timestamp ASC
            """
            
            cursor.execute(query, (analysis_id,))
            rows = cursor.fetchall()
            
            return [
                {
                    'question': row['question'],
                    'answer': row['answer'],
                    'timestamp': row['timestamp']
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting follow-up questions: {str(e)}")
            return []
    
    async def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis results"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT analysis_id, timestamp, created_at FROM analysis_results 
            ORDER BY created_at DESC LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            return [
                {
                    'analysis_id': row['analysis_id'],
                    'timestamp': row['timestamp'],
                    'created_at': row['created_at']
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent analyses: {str(e)}")
            return []
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis result and related data"""
        try:
            cursor = self.connection.cursor()
            
            # Delete follow-up questions first
            cursor.execute("DELETE FROM follow_up_questions WHERE analysis_id = ?", (analysis_id,))
            
            # Delete analysis result
            cursor.execute("DELETE FROM analysis_results WHERE analysis_id = ?", (analysis_id,))
            
            self.connection.commit()
            
            logger.info(f"Analysis deleted: {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis: {str(e)}")
            return False
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Count total analyses
            cursor.execute("SELECT COUNT(*) as total FROM analysis_results")
            total_analyses = cursor.fetchone()['total']
            
            # Count analyses by date
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM analysis_results 
                GROUP BY DATE(created_at) 
                ORDER BY date DESC 
                LIMIT 7
            """)
            daily_counts = cursor.fetchall()
            
            # Count follow-up questions
            cursor.execute("SELECT COUNT(*) as total FROM follow_up_questions")
            total_questions = cursor.fetchone()['total']
            
            return {
                'total_analyses': total_analyses,
                'total_follow_up_questions': total_questions,
                'daily_analyses': [
                    {'date': row['date'], 'count': row['count']} 
                    for row in daily_counts
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'total_analyses': 0, 'total_follow_up_questions': 0, 'daily_analyses': []}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")