import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Shield, AlertTriangle, TrendingUp, Info } from 'lucide-react';

interface Disease {
  name: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
}

interface DiseaseDetectionProps {
  diseases: Disease[];
}

export const DiseaseDetection: React.FC<DiseaseDetectionProps> = ({ diseases }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-medical-red" />;
      case 'medium':
        return <TrendingUp className="h-4 w-4 text-medical-orange" />;
      case 'low':
        return <Info className="h-4 w-4 text-medical-blue" />;
      default:
        return <Shield className="h-4 w-4 text-medical-green" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-medical-red text-white';
      case 'medium':
        return 'bg-medical-orange text-white';
      case 'low':
        return 'bg-medical-blue text-white';
      default:
        return 'bg-medical-green text-white';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-medical-red';
    if (confidence >= 60) return 'text-medical-orange';
    if (confidence >= 40) return 'text-medical-blue';
    return 'text-muted-foreground';
  };

  const getProgressColor = (confidence: number) => {
    if (confidence >= 80) return 'bg-medical-red';
    if (confidence >= 60) return 'bg-medical-orange';
    if (confidence >= 40) return 'bg-medical-blue';
    return 'bg-muted';
  };

  const sortedDiseases = [...diseases].sort((a, b) => b.confidence - a.confidence);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          Disease Detection & Risk Assessment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedDiseases.length === 0 ? (
            <div className="text-center py-8">
              <div className="p-4 bg-medical-green/10 rounded-xl w-fit mx-auto mb-4">
                <Shield className="h-8 w-8 text-medical-green" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                No Significant Abnormalities Detected
              </h3>
              <p className="text-muted-foreground">
                The blood sample shows normal cellular patterns and counts.
              </p>
            </div>
          ) : (
            <>
              <div className="text-sm text-muted-foreground mb-4">
                AI confidence scores based on cellular morphology and count analysis
              </div>
              
              {sortedDiseases.map((disease, index) => (
                <div key={index} className="p-4 border border-border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getSeverityIcon(disease.severity)}
                      <div>
                        <h4 className="font-semibold text-foreground">{disease.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {disease.severity.charAt(0).toUpperCase() + disease.severity.slice(1)} severity risk
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getSeverityColor(disease.severity)}>
                        {disease.severity.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Confidence Score</span>
                      <span className={`text-lg font-bold ${getConfidenceColor(disease.confidence)}`}>
                        {disease.confidence}%
                      </span>
                    </div>
                    <div className="relative">
                      <Progress 
                        value={disease.confidence} 
                        className="h-2"
                      />
                      <style>{`
                        .progress-bar-${index} {
                          background-color: ${
                            disease.confidence >= 80 ? 'hsl(var(--medical-red))' :
                            disease.confidence >= 60 ? 'hsl(var(--medical-orange))' :
                            disease.confidence >= 40 ? 'hsl(var(--medical-blue))' :
                            'hsl(var(--muted))'
                          };
                        }
                      `}</style>
                    </div>
                  </div>
                  
                  {/* Additional Information */}
                  <div className="pt-3 border-t border-border">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Detection Method:</span>
                        <p className="font-medium">Deep Learning Analysis</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Recommendation:</span>
                        <p className="font-medium">
                          {disease.confidence >= 70 
                            ? 'Consult specialist' 
                            : disease.confidence >= 50 
                            ? 'Monitor closely' 
                            : 'Routine follow-up'
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
          
          {/* Disclaimer */}
          <div className="mt-6 p-4 bg-muted/50 rounded-lg border border-border">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div className="text-sm space-y-1">
                <p className="font-medium text-foreground">Medical Disclaimer</p>
                <p className="text-muted-foreground">
                  This AI analysis is for research and educational purposes only. 
                  Always consult with qualified healthcare professionals for medical diagnosis and treatment decisions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};