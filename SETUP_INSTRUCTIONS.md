# BloodCell AI - Setup Instructions

## Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm/bun
- Git

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the backend server
```bash
python main.py
```

The backend will start at `http://localhost:8000`

### Alternative: Using Docker
```bash
cd backend
docker-compose up --build
```

## Frontend Setup

### 1. Navigate to root directory (where package.json is)
```bash
cd ..  # if you're in backend directory
```

### 2. Install dependencies
```bash
npm install
# or
bun install
```

### 3. Start development server
```bash
npm run dev
# or
bun dev
```

The frontend will start at `http://localhost:5173`

## Testing the Integration

1. Make sure both servers are running:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:5173`

2. Visit `http://localhost:5173` in your browser

3. Upload a blood smear image to test the AI analysis

## Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change port in `backend/main.py` line 230
- **Dependencies missing**: Ensure virtual environment is activated
- **CORS errors**: Backend is configured for localhost:5173

### Frontend Issues
- **Failed to fetch**: Ensure backend is running on port 8000
- **Connection refused**: Check if backend server started successfully

### Performance Notes
- First AI model load takes 30-60 seconds
- Subsequent analyses are faster (~5-10 seconds)
- GPU acceleration available if CUDA is installed

## Production Deployment

### Backend
```bash
cd backend
docker build -t bloodcell-ai-backend .
docker run -p 8000:8000 bloodcell-ai-backend
```

### Frontend
```bash
npm run build
# Deploy dist/ folder to your hosting service
```