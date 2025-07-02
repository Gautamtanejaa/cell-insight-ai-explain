from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import uuid
import asyncio
from typing import Dict, List
import logging
from pathlib import Path

from services.image_processor import ImageProcessor
from services.analysis_service import AnalysisService
from models.efficientnet_model import EfficientNetB0Model
from models.medical_llama import MedicalLLaMA
from database import Database, AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BloodCell AI Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
image_processor = ImageProcessor()
analysis_service = AnalysisService()
db = Database()

# AI Models (loaded on startup)
efficientnet_model = None
medical_llama = None

# Store analysis progress
analysis_progress: Dict[str, dict] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    global efficientnet_model, medical_llama
    
    logger.info("Loading AI models...")
    
    # Load EfficientNet B0 model
    efficientnet_model = EfficientNetB0Model()
    await efficientnet_model.load_model()
    
    # Load Medical LLaMA model
    medical_llama = MedicalLLaMA()
    await medical_llama.load_model()
    
    # Initialize database
    await db.init_db()
    
    logger.info("AI models loaded successfully!")

@app.get("/")
async def root():
    return {"message": "BloodCell AI Backend is running"}

@app.post("/api/upload")
async def upload_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and validate blood smear image"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / f"{analysis_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize analysis progress
        analysis_progress[analysis_id] = {
            "status": "uploaded",
            "progress": 10,
            "stage": "Image uploaded successfully"
        }
        
        # Start background analysis
        background_tasks.add_task(perform_analysis, analysis_id, str(file_path))
        
        return {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Image uploaded successfully. Analysis started."
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/api/progress/{analysis_id}")
async def get_analysis_progress(analysis_id: str):
    """Get real-time analysis progress"""
    
    if analysis_id not in analysis_progress:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_progress[analysis_id]

@app.get("/api/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get complete analysis results"""
    
    result = await db.get_analysis_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    return result

@app.post("/api/medical-explanation/{analysis_id}")
async def generate_medical_explanation(analysis_id: str):
    """Generate AI-powered medical explanation"""
    
    # Get analysis results
    result = await db.get_analysis_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    try:
        # Generate medical explanation using LLaMA
        explanation = await medical_llama.generate_explanation(result)
        
        # Update database with explanation
        await db.update_analysis_explanation(analysis_id, explanation)
        
        return {"explanation": explanation}
        
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

async def perform_analysis(analysis_id: str, image_path: str):
    """Background task to perform complete blood cell analysis"""
    
    try:
        # Update progress: Image preprocessing
        analysis_progress[analysis_id].update({
            "status": "preprocessing",
            "progress": 20,
            "stage": "Preprocessing image..."
        })
        
        # Preprocess image
        processed_image = await image_processor.preprocess_image(image_path)
        
        # Update progress: EfficientNet analysis
        analysis_progress[analysis_id].update({
            "status": "analyzing",
            "progress": 40,
            "stage": "EfficientNet B0 analysis..."
        })
        
        # Perform EfficientNet B0 analysis
        cell_analysis = await efficientnet_model.analyze_cells(processed_image)
        
        # Update progress: Disease detection
        analysis_progress[analysis_id].update({
            "status": "detecting",
            "progress": 70,
            "stage": "Disease detection..."
        })
        
        # Perform disease detection
        disease_results = await analysis_service.detect_diseases(cell_analysis)
        
        # Update progress: Finalizing
        analysis_progress[analysis_id].update({
            "status": "finalizing",
            "progress": 90,
            "stage": "Finalizing results..."
        })
        
        # Prepare final results
        final_results = {
            "analysis_id": analysis_id,
            "cell_counts": cell_analysis["cell_counts"],
            "diseases": disease_results["diseases"],
            "abnormalities": disease_results["abnormalities"],
            "confidence_scores": cell_analysis["confidence_scores"],
            "image_path": image_path,
            "timestamp": cell_analysis["timestamp"]
        }
        
        # Save to database
        await db.save_analysis_result(AnalysisResult(**final_results))
        
        # Update progress: Complete
        analysis_progress[analysis_id].update({
            "status": "completed",
            "progress": 100,
            "stage": "Analysis completed successfully!"
        })
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in analysis {analysis_id}: {str(e)}")
        analysis_progress[analysis_id].update({
            "status": "error",
            "progress": 0,
            "stage": f"Analysis failed: {str(e)}"
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)