import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart3, TrendingUp, AlertCircle } from 'lucide-react';

interface CellCounts {
  neutrophils: number;
  lymphocytes: number;
  monocytes: number;
  eosinophils: number;
  basophils: number;
  platelets: number;
  rbcs: number;
}

interface AnalysisResultsProps {
  cellCounts: CellCounts;
  abnormalities: string[];
  imageUrl: string | null;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ 
  cellCounts, 
  abnormalities, 
  imageUrl 
}) => {
  const getCellColor = (cellType: string) => {
    const colors = {
      neutrophils: 'bg-medical-blue',
      lymphocytes: 'bg-medical-green',
      monocytes: 'bg-medical-orange',
      eosinophils: 'bg-medical-red',
      basophils: 'bg-purple-500'
    };
    return colors[cellType as keyof typeof colors] || 'bg-gray-500';
  };

  const getNormalRange = (cellType: string) => {
    const ranges = {
      neutrophils: { min: 50, max: 70, unit: '%' },
      lymphocytes: { min: 20, max: 45, unit: '%' },
      monocytes: { min: 2, max: 10, unit: '%' },
      eosinophils: { min: 1, max: 6, unit: '%' },
      basophils: { min: 0, max: 2, unit: '%' },
      platelets: { min: 150000, max: 450000, unit: '/μL' },
      rbcs: { min: 4200000, max: 5400000, unit: '/μL' }
    };
    return ranges[cellType as keyof typeof ranges];
  };

  const getStatusBadge = (value: number, cellType: string) => {
    const range = getNormalRange(cellType);
    if (!range) return <Badge variant="secondary">Unknown</Badge>;

    if (value < range.min) {
      return <Badge className="bg-medical-red text-white">Low</Badge>;
    } else if (value > range.max) {
      return <Badge className="bg-medical-orange text-white">High</Badge>;
    } else {
      return <Badge className="bg-medical-green text-white">Normal</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Original Image */}
      {imageUrl && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🔬 Original Blood Smear
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative rounded-lg overflow-hidden">
              <img 
                src={imageUrl} 
                alt="Blood smear analysis" 
                className="w-full h-64 object-cover"
              />
              <div className="absolute top-4 right-4">
                <Badge className="bg-primary text-primary-foreground">
                  Analyzed by EfficientNet B0
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cell Count Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Cell Count Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* White Blood Cells */}
            <div>
              <h4 className="font-semibold mb-4 text-foreground">White Blood Cell Differential</h4>
              <div className="grid gap-4">
                {['neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils'].map((cellType) => {
                  const value = cellCounts[cellType as keyof CellCounts] as number;
                  const range = getNormalRange(cellType);
                  const percentage = range ? Math.min((value / range.max) * 100, 100) : 0;
                  
                  return (
                    <div key={cellType} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${getCellColor(cellType)}`} />
                          <span className="font-medium capitalize">{cellType}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold">{value}%</span>
                          {getStatusBadge(value, cellType)}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={percentage} className="flex-1 h-2" />
                        <span className="text-xs text-muted-foreground min-w-fit">
                          Normal: {range?.min}-{range?.max}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Other Cell Counts */}
            <div className="pt-4 border-t border-border">
              <h4 className="font-semibold mb-4 text-foreground">Complete Blood Count</h4>
              <div className="grid md:grid-cols-2 gap-4">
                {['platelets', 'rbcs'].map((cellType) => {
                  const value = cellCounts[cellType as keyof CellCounts] as number;
                  const range = getNormalRange(cellType);
                  
                  return (
                    <div key={cellType} className="p-4 bg-muted/50 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium capitalize">
                          {cellType === 'rbcs' ? 'Red Blood Cells' : 'Platelets'}
                        </span>
                        {getStatusBadge(value, cellType)}
                      </div>
                      <div className="text-2xl font-bold text-foreground">
                        {value.toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Normal: {range?.min.toLocaleString()}-{range?.max.toLocaleString()} {range?.unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Abnormalities */}
      {abnormalities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-warning" />
              Detected Abnormalities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {abnormalities.map((abnormality, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-warning/10 rounded-lg border border-warning/20">
                  <div className="w-2 h-2 rounded-full bg-warning mt-2 flex-shrink-0" />
                  <div>
                    <p className="text-foreground">{abnormality}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
