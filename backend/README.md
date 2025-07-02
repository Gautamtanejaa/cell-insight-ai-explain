# BloodCell AI Backend

## Overview
Advanced blood cell analysis backend using EfficientNet B0 for computer vision and Medical LLaMA for AI-powered medical explanations.

## Features
- **EfficientNet B0 Model**: Blood cell classification and counting
- **Medical LLaMA**: AI-powered medical explanations and insights
- **Real-time Analysis**: Progress tracking and WebSocket support
- **Disease Detection**: Pattern recognition for various conditions
- **RESTful API**: Complete API for frontend integration
- **Database Storage**: SQLite for results persistence

## Installation

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build

# Or build manually
docker build -t bloodcell-ai-backend .
docker run -p 8000:8000 bloodcell-ai-backend
```

## API Endpoints

### Image Upload and Analysis
- `POST /api/upload` - Upload blood smear image for analysis
- `GET /api/progress/{analysis_id}` - Get real-time analysis progress
- `GET /api/results/{analysis_id}` - Get complete analysis results

### Medical AI
- `POST /api/medical-explanation/{analysis_id}` - Generate medical explanation
- `POST /api/follow-up-question` - Ask follow-up questions

### Health Check
- `GET /` - API health check

## Models

### EfficientNet B0
- **Purpose**: Blood cell classification and detection
- **Input**: 224x224 RGB images
- **Output**: Cell counts, classifications, confidence scores
- **Classes**: Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Platelets, RBCs

### Medical LLaMA
- **Purpose**: Medical explanation generation
- **Model**: BioGPT-Large (or similar medical model)
- **Features**: Context-aware medical reasoning, disease explanation, follow-up Q&A

## Disease Detection

The system can detect:
- Bacterial infections (neutrophilia pattern)
- Viral infections (lymphocytosis pattern)  
- Anemia (low RBC count)
- Leukocytosis (elevated WBC)
- Thrombocytopenia (low platelets)
- Various morphological abnormalities

## Configuration

### Environment Variables
```bash
# Optional configuration
ENVIRONMENT=development  # or production
DATABASE_URL=sqlite:///bloodcell_analysis.db
MODEL_CACHE_DIR=./models
UPLOAD_DIR=./uploads
```

### Model Configuration
Models are automatically downloaded on first run:
- EfficientNet B0: Pre-trained on ImageNet, fine-tuned for blood cells
- Medical LLaMA: BioGPT-Large from Hugging Face

## Development

### Project Structure
```
backend/
├── main.py                 # FastAPI application
├── models/
│   ├── efficientnet_model.py   # EfficientNet B0 implementation
│   └── medical_llama.py        # Medical LLaMA integration
├── services/
│   ├── image_processor.py      # Image preprocessing
│   └── analysis_service.py     # Disease detection logic
├── database.py             # SQLite database layer
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Multi-container setup
```

### Adding New Models
1. Create model class in `models/` directory
2. Implement `load_model()` and prediction methods
3. Update `main.py` to initialize new model
4. Add model-specific endpoints as needed

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Test specific endpoint
curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_image.jpg"
```

## Performance

### Optimization Tips
- Use GPU acceleration for faster inference
- Implement model caching for repeated requests
- Use async/await for concurrent processing
- Consider model quantization for production

### Monitoring
- Health checks available at `/`
- Logging configured for production use
- Database statistics endpoint available

## Security

### Important Considerations
- Validate all uploaded images
- Implement rate limiting for API endpoints
- Use secure file handling practices
- Consider authentication for production use

## License
This project is for educational and research purposes. Medical AI should not be used for actual diagnosis without proper clinical validation.

## Support
For questions or issues, please refer to the project documentation or contact the development team.