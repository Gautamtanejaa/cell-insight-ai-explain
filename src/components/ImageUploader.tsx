import React, { useCallback, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, Image as ImageIcon, FileText } from 'lucide-react';

interface ImageUploaderProps {
  onImageUpload: (imageUrl: string) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageUpload }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFile = (file: File) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          onImageUpload(e.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleSampleUpload = () => {
    // For demo purposes, use a placeholder blood sample image
    const sampleImageUrl = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRkZGNUY1Ii8+CjxjaXJjbGUgY3g9IjEwMCIgY3k9IjEwMCIgcj0iMTUiIGZpbGw9IiNEQzI2MjYiIG9wYWNpdHk9IjAuOCIvPgo8Y2lyY2xlIGN4PSIyMDAiIGN5PSIxNTAiIHI9IjEyIiBmaWxsPSIjMTZBMzRBIiBvcGFjaXR5PSIwLjciLz4KPGV2Y2dsZSBjeD0iMzAwIiBjeT0iMTIwIiByeD0iMjAiIHJ5PSIxMCIgZmlsbD0iIzIzNjNFQiIgb3BhY2l0eT0iMC42Ii8+CjxjaXJjbGUgY3g9IjE1MCIgY3k9IjIwMCIgcj0iOCIgZmlsbD0iI0Y1OTUwOCIgb3BhY2l0eT0iMC43Ii8+CjxjaXJjbGUgY3g9IjI1MCIgY3k9IjgwIiByPSI2IiBmaWxsPSIjNzMxQ0Y4IiBvcGFjaXR5PSIwLjgiLz4KPHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeD0iMzAiIHk9IjIwIj4KICA8cGF0aCBkPSJNMjAgNEwzMCAyMEgyMEwxMCAyMFoiIGZpbGw9IiNEQzI2MjYiIG9wYWNpdHk9IjAuNiIvPgo8L3N2Zz4KPHR4dCB4PSIyMDAiIHk9IjI3MCIgZmlsbD0iIzY0NzQ4QiIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk1vY2sgQmxvb2QgU21lYXI8L3R4dD4KPC9zdmc+";
    onImageUpload(sampleImageUrl);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="overflow-hidden">
        <CardContent className="p-8">
          <div
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
              dragActive
                ? 'border-primary bg-primary/5 scale-105'
                : 'border-border hover:border-primary/50 hover:bg-muted/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="space-y-6">
              <div className="flex justify-center">
                <div className="p-4 bg-gradient-primary rounded-xl">
                  <Upload className="h-12 w-12 text-white" />
                </div>
              </div>
              
              <div className="space-y-2">
                <h3 className="text-2xl font-semibold text-foreground">
                  Upload Blood Smear Image
                </h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                  Drag and drop your blood smear microscopy image here, or click to browse files
                </p>
              </div>

              <div className="space-y-4">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleInputChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button asChild className="bg-gradient-primary hover:opacity-90 transition-opacity">
                    <span className="cursor-pointer">
                      <ImageIcon className="mr-2 h-4 w-4" />
                      Choose Image File
                    </span>
                  </Button>
                </label>

                <div className="text-sm text-muted-foreground">
                  Supported formats: JPEG, PNG, TIFF (Max size: 10MB)
                </div>
              </div>
            </div>
          </div>

          {/* Sample Data Section */}
          <div className="mt-8 pt-8 border-t border-border">
            <div className="text-center space-y-4">
              <h4 className="text-lg font-medium text-foreground">
                Try with Sample Data
              </h4>
              <p className="text-muted-foreground text-sm">
                Don't have a blood smear image? Use our sample data to explore the analysis features
              </p>
              <Button 
                variant="outline" 
                onClick={handleSampleUpload}
                className="border-primary text-primary hover:bg-primary hover:text-primary-foreground"
              >
                <FileText className="mr-2 h-4 w-4" />
                Load Sample Blood Smear
              </Button>
            </div>
          </div>

          {/* Technical Requirements */}
          <div className="mt-8 pt-8 border-t border-border">
            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div className="text-center space-y-2">
                <div className="p-2 bg-medical-blue/10 rounded-lg w-fit mx-auto">
                  🔬
                </div>
                <h5 className="font-medium">High Quality Images</h5>
                <p className="text-muted-foreground">
                  Use high-resolution microscopy images (minimum 1000x1000 pixels)
                </p>
              </div>
              <div className="text-center space-y-2">
                <div className="p-2 bg-medical-green/10 rounded-lg w-fit mx-auto">
                  🎯
                </div>
                <h5 className="font-medium">Proper Staining</h5>
                <p className="text-muted-foreground">
                  Ensure images are properly stained with Wright-Giemsa or similar
                </p>
              </div>
              <div className="text-center space-y-2">
                <div className="p-2 bg-medical-orange/10 rounded-lg w-fit mx-auto">
                  ⚡
                </div>
                <h5 className="font-medium">Fast Processing</h5>
                <p className="text-muted-foreground">
                  Analysis typically completed within 10-30 seconds
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};