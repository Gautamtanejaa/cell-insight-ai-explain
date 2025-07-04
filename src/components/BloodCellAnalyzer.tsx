import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Upload, Microscope, Brain, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { ImageUploader } from './ImageUploader';
import { AnalysisResults } from './AnalysisResults';
import { DiseaseDetection } from './DiseaseDetection';
import { MedicalExplanation } from './MedicalExplanation';

interface AnalysisData {
  analysisId: string;
  cellCounts: {
    neutrophils: number;
    lymphocytes: number;
    monocytes: number;
    eosinophils: number;
    basophils: number;
    platelets: number;
    rbcs: number;
  };
  diseases: {
    name: string;
    confidence: number;
    severity: 'low' | 'medium' | 'high';
  }[];
  abnormalities: string[];
}

export const BloodCellAnalyzer = () => {
  const [currentStep, setCurrentStep] = useState<'upload' | 'analyzing' | 'results'>('upload');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);

  const handleImageUpload = async (imageUrl: string) => {
    setUploadedImage(imageUrl);
    
    // Convert data URL to blob for upload
    const blob = await dataURLToBlob(imageUrl);
    const file = new File([blob], 'blood_sample.jpg', { type: 'image/jpeg' });
    
    await startAnalysis(file);
  };

  const dataURLToBlob = (dataURL: string): Promise<Blob> => {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx?.drawImage(img, 0, 0);
        canvas.toBlob((blob) => {
          resolve(blob!);
        }, 'image/jpeg', 0.8);
      };
      
      img.src = dataURL;
    });
  };

  const startAnalysis = async (file: File) => {
    setCurrentStep('analyzing');
    setAnalysisProgress(0);

    try {
      // Upload image to backend
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload image');
      }

      const uploadResult = await uploadResponse.json();
      const analysisId = uploadResult.analysis_id;

      // Poll for progress
      await pollAnalysisProgress(analysisId);
      
    } catch (error) {
      console.error('Analysis error:', error);
      setCurrentStep('upload');
      // Show error message to user
      alert('Failed to analyze image. Please try again.');
    }
  };

  const pollAnalysisProgress = async (analysisId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const progressResponse = await fetch(`http://localhost:8000/api/progress/${analysisId}`);
        const progressData = await progressResponse.json();

        setAnalysisProgress(progressData.progress);

        if (progressData.status === 'completed') {
          clearInterval(pollInterval);
          await fetchAnalysisResults(analysisId);
        } else if (progressData.status === 'error') {
          clearInterval(pollInterval);
          console.error('Analysis failed:', progressData.stage);
          setCurrentStep('upload');
          alert('Analysis failed: ' + progressData.stage);
        }
      } catch (error) {
        clearInterval(pollInterval);
        console.error('Progress polling error:', error);
        setCurrentStep('upload');
        alert('Connection error. Please check if backend is running.');
      }
    }, 1000);
  };

  const fetchAnalysisResults = async (analysisId: string) => {
    try {
      const resultsResponse = await fetch(`http://localhost:8000/api/results/${analysisId}`);
      const results = await resultsResponse.json();

      const analysisData: AnalysisData = {
        analysisId: analysisId,
        cellCounts: results.cell_counts,
        diseases: results.diseases,
        abnormalities: results.abnormalities
      };

      setAnalysisData(analysisData);
      setCurrentStep('results');
    } catch (error) {
      console.error('Error fetching results:', error);
      setCurrentStep('upload');
      alert('Failed to fetch results. Please try again.');
    }
  };


  const resetAnalysis = () => {
    setCurrentStep('upload');
    setUploadedImage(null);
    setAnalysisData(null);
    setAnalysisProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-analysis p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-primary rounded-xl">
              <Microscope className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-foreground">BloodCell AI</h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Advanced blood cell analysis using EfficientNet B0 deep learning with AI-powered medical insights
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center gap-4">
            {[
              { step: 'upload', icon: Upload, label: 'Upload Image' },
              { step: 'analyzing', icon: Clock, label: 'AI Analysis' },
              { step: 'results', icon: CheckCircle, label: 'Results' }
            ].map(({ step, icon: Icon, label }, index) => (
              <div key={step} className="flex items-center gap-4">
                <div className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentStep === step 
                    ? 'bg-primary text-primary-foreground shadow-lg' 
                    : index < ['upload', 'analyzing', 'results'].indexOf(currentStep)
                    ? 'bg-accent text-accent-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}>
                  <Icon className="h-4 w-4" />
                  <span className="font-medium">{label}</span>
                </div>
                {index < 2 && (
                  <div className={`w-8 h-0.5 transition-all ${
                    index < ['upload', 'analyzing', 'results'].indexOf(currentStep)
                      ? 'bg-accent'
                      : 'bg-border'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        {currentStep === 'upload' && (
          <ImageUploader onImageUpload={handleImageUpload} />
        )}

        {currentStep === 'analyzing' && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center gap-2">
                <Brain className="h-6 w-6 text-primary animate-pulse" />
                Analyzing Blood Sample
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {uploadedImage && (
                <div className="relative overflow-hidden rounded-lg">
                  <img 
                    src={uploadedImage} 
                    alt="Blood sample" 
                    className="w-full h-48 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/20 to-transparent animate-scan" />
                </div>
              )}
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>EfficientNet B0 Analysis</span>
                  <span>{analysisProgress}%</span>
                </div>
                <Progress value={analysisProgress} className="h-2" />
                
                <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                  <div>🔬 Cell Detection</div>
                  <div>🧬 Feature Extraction</div>
                  <div>🔍 Morphology Analysis</div>
                  <div>🤖 AI Classification</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {currentStep === 'results' && analysisData && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <AnalysisResults 
                cellCounts={analysisData.cellCounts}
                abnormalities={analysisData.abnormalities}
                imageUrl={uploadedImage}
              />
              <DiseaseDetection diseases={analysisData.diseases} />
            </div>
            <div className="space-y-6">
              <MedicalExplanation 
                analysisData={analysisData}
                onNewAnalysis={resetAnalysis}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};