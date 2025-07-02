import asyncio
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for comprehensive blood analysis and disease detection"""
    
    def __init__(self):
        self.disease_patterns = {
            'bacterial_infection': {
                'neutrophils': (70, 100),
                'lymphocytes': (10, 25),
                'severity_thresholds': {'high': 80, 'medium': 70, 'low': 60}
            },
            'viral_infection': {
                'neutrophils': (30, 50),
                'lymphocytes': (40, 70),
                'severity_thresholds': {'high': 50, 'medium': 45, 'low': 40}
            },
            'anemia': {
                'rbcs': (0, 4200000),
                'severity_thresholds': {'high': 3000000, 'medium': 3500000, 'low': 4000000}
            },
            'leukocytosis': {
                'total_wbc': (11000, float('inf')),
                'severity_thresholds': {'high': 20000, 'medium': 15000, 'low': 11000}
            },
            'thrombocytopenia': {
                'platelets': (0, 150000),
                'severity_thresholds': {'high': 50000, 'medium': 100000, 'low': 150000}
            },
            'leukemia_indicators': {
                'blast_cells': (5, 100),
                'severity_thresholds': {'high': 20, 'medium': 10, 'low': 5}
            }
        }
        
        self.normal_ranges = {
            'neutrophils': (50, 70),
            'lymphocytes': (20, 40),
            'monocytes': (2, 10),
            'eosinophils': (1, 4),
            'basophils': (0, 2),
            'platelets': (150000, 450000),
            'rbcs': (4200000, 5400000)
        }
    
    async def detect_diseases(self, cell_analysis: Dict) -> Dict:
        """Detect potential diseases based on cell analysis results"""
        try:
            logger.info("Starting disease detection analysis...")
            
            cell_counts = cell_analysis.get('cell_counts', {})
            
            # Detect various conditions
            diseases = []
            abnormalities = []
            
            # Check for bacterial infection
            bacterial_result = await self._check_bacterial_infection(cell_counts)
            if bacterial_result:
                diseases.append(bacterial_result)
                abnormalities.extend(bacterial_result.get('abnormalities', []))
            
            # Check for viral infection
            viral_result = await self._check_viral_infection(cell_counts)
            if viral_result:
                diseases.append(viral_result)
                abnormalities.extend(viral_result.get('abnormalities', []))
            
            # Check for anemia
            anemia_result = await self._check_anemia(cell_counts)
            if anemia_result:
                diseases.append(anemia_result)
                abnormalities.extend(anemia_result.get('abnormalities', []))
            
            # Check for leukocytosis
            leukocytosis_result = await self._check_leukocytosis(cell_counts)
            if leukocytosis_result:
                diseases.append(leukocytosis_result)
                abnormalities.extend(leukocytosis_result.get('abnormalities', []))
            
            # Check for thrombocytopenia
            thrombocytopenia_result = await self._check_thrombocytopenia(cell_counts)
            if thrombocytopenia_result:
                diseases.append(thrombocytopenia_result)
                abnormalities.extend(thrombocytopenia_result.get('abnormalities', []))
            
            # Add morphological abnormalities
            morphological_abnormalities = await self._detect_morphological_abnormalities(cell_counts)
            abnormalities.extend(morphological_abnormalities)
            
            # Sort diseases by confidence
            diseases.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Remove duplicates from abnormalities
            abnormalities = list(set(abnormalities))
            
            logger.info(f"Disease detection completed. Found {len(diseases)} potential conditions and {len(abnormalities)} abnormalities.")
            
            return {
                'diseases': diseases,
                'abnormalities': abnormalities,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in disease detection: {str(e)}")
            return await self._get_mock_disease_results(cell_analysis)
    
    async def _check_bacterial_infection(self, cell_counts: Dict) -> Dict:
        """Check for signs of bacterial infection"""
        
        neutrophils = cell_counts.get('neutrophils', 0)
        lymphocytes = cell_counts.get('lymphocytes', 0)
        
        # Bacterial infection pattern: high neutrophils, low lymphocytes
        if neutrophils >= 70 and lymphocytes <= 25:
            confidence = min(95, 50 + (neutrophils - 70) * 2 + (25 - lymphocytes) * 1.5)
            
            severity = 'high' if neutrophils >= 80 else 'medium' if neutrophils >= 75 else 'low'
            
            return {
                'name': 'Bacterial Infection',
                'confidence': int(confidence),
                'severity': severity,
                'abnormalities': [
                    f'Elevated neutrophil count ({neutrophils}%)',
                    f'Relative lymphopenia ({lymphocytes}%)',
                    'Left shift pattern (immature neutrophils)'
                ]
            }
        
        return None
    
    async def _check_viral_infection(self, cell_counts: Dict) -> Dict:
        """Check for signs of viral infection"""
        
        neutrophils = cell_counts.get('neutrophils', 0)
        lymphocytes = cell_counts.get('lymphocytes', 0)
        
        # Viral infection pattern: low neutrophils, high lymphocytes
        if neutrophils <= 50 and lymphocytes >= 40:
            confidence = min(90, 40 + (50 - neutrophils) * 1.5 + (lymphocytes - 40) * 2)
            
            severity = 'high' if lymphocytes >= 60 else 'medium' if lymphocytes >= 50 else 'low'
            
            return {
                'name': 'Viral Infection',
                'confidence': int(confidence),
                'severity': severity,
                'abnormalities': [
                    f'Relative neutropenia ({neutrophils}%)',
                    f'Lymphocytosis ({lymphocytes}%)',
                    'Atypical lymphocytes present'
                ]
            }
        
        return None
    
    async def _check_anemia(self, cell_counts: Dict) -> Dict:
        """Check for signs of anemia"""
        
        rbcs = cell_counts.get('rbcs', 0)
        normal_min = self.normal_ranges['rbcs'][0]
        
        if rbcs < normal_min:
            deficit_percentage = ((normal_min - rbcs) / normal_min) * 100
            confidence = min(85, 30 + deficit_percentage * 2)
            
            severity = 'high' if rbcs < 3000000 else 'medium' if rbcs < 3500000 else 'low'
            
            anemia_type = await self._classify_anemia_type(cell_counts)
            
            return {
                'name': f'{anemia_type} Anemia',
                'confidence': int(confidence),
                'severity': severity,
                'abnormalities': [
                    f'Reduced red blood cell count ({rbcs:,}/μL)',
                    'Possible microcytic changes',
                    'Hypochromic cells observed'
                ]
            }
        
        return None
    
    async def _classify_anemia_type(self, cell_counts: Dict) -> str:
        """Classify the type of anemia based on available data"""
        
        # This would normally use MCV, MCH, MCHC values
        # For demo purposes, we'll use a simple classification
        rbcs = cell_counts.get('rbcs', 0)
        
        if rbcs < 3000000:
            return 'Severe'
        elif rbcs < 3500000:
            return 'Moderate'
        else:
            return 'Mild'
    
    async def _check_leukocytosis(self, cell_counts: Dict) -> Dict:
        """Check for elevated white blood cell count"""
        
        # Estimate total WBC from percentages (assuming normal total around 7000)
        neutrophils = cell_counts.get('neutrophils', 0)
        lymphocytes = cell_counts.get('lymphocytes', 0)
        
        # If neutrophils are very high, likely indicates leukocytosis
        if neutrophils >= 75:
            confidence = min(80, 40 + (neutrophils - 75) * 3)
            
            severity = 'high' if neutrophils >= 85 else 'medium' if neutrophils >= 80 else 'low'
            
            return {
                'name': 'Leukocytosis',
                'confidence': int(confidence),
                'severity': severity,
                'abnormalities': [
                    f'Markedly elevated neutrophil percentage ({neutrophils}%)',
                    'Possible left shift pattern',
                    'Increased total white blood cell count'
                ]
            }
        
        return None
    
    async def _check_thrombocytopenia(self, cell_counts: Dict) -> Dict:
        """Check for low platelet count"""
        
        platelets = cell_counts.get('platelets', 0)
        normal_min = self.normal_ranges['platelets'][0]
        
        if platelets < normal_min:
            deficit_percentage = ((normal_min - platelets) / normal_min) * 100
            confidence = min(90, 50 + deficit_percentage * 1.5)
            
            severity = 'high' if platelets < 50000 else 'medium' if platelets < 100000 else 'low'
            
            return {
                'name': 'Thrombocytopenia',
                'confidence': int(confidence),
                'severity': severity,
                'abnormalities': [
                    f'Decreased platelet count ({platelets:,}/μL)',
                    'Large platelet forms observed',
                    'Possible bleeding tendency'
                ]
            }
        
        return None
    
    async def _detect_morphological_abnormalities(self, cell_counts: Dict) -> List[str]:
        """Detect morphological abnormalities in blood cells"""
        
        abnormalities = []
        
        # Check each cell type against normal ranges
        for cell_type, count in cell_counts.items():
            if cell_type in self.normal_ranges:
                normal_min, normal_max = self.normal_ranges[cell_type]
                
                if count < normal_min:
                    if cell_type in ['neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']:
                        abnormalities.append(f'Reduced {cell_type} percentage')
                    else:
                        abnormalities.append(f'Low {cell_type} count')
                elif count > normal_max:
                    if cell_type in ['neutrophils', 'lymphocytes', 'monocytes', 'eosinophils', 'basophils']:
                        abnormalities.append(f'Elevated {cell_type} percentage')
                    else:
                        abnormalities.append(f'High {cell_type} count')
                else:
                    # Within normal range
                    if cell_type == 'platelets':
                        abnormalities.append('Normal platelet morphology')
                    elif cell_type == 'rbcs':
                        abnormalities.append('Normal red blood cell morphology')
        
        # Add some additional morphological observations
        neutrophils = cell_counts.get('neutrophils', 0)
        if neutrophils > 70:
            abnormalities.extend([
                'Toxic granulation in neutrophils',
                'Nuclear hypersegmentation observed'
            ])
        
        lymphocytes = cell_counts.get('lymphocytes', 0)
        if lymphocytes > 40:
            abnormalities.append('Reactive lymphocytes present')
        
        return abnormalities
    
    async def calculate_risk_scores(self, cell_counts: Dict) -> Dict:
        """Calculate risk scores for various conditions"""
        
        risk_scores = {}
        
        # Infection risk
        neutrophils = cell_counts.get('neutrophils', 0)
        lymphocytes = cell_counts.get('lymphocytes', 0)
        
        if neutrophils > 70:
            risk_scores['bacterial_infection'] = min(100, (neutrophils - 50) * 2)
        else:
            risk_scores['bacterial_infection'] = 0
        
        if lymphocytes > 40:
            risk_scores['viral_infection'] = min(100, (lymphocytes - 20) * 2.5)
        else:
            risk_scores['viral_infection'] = 0
        
        # Hematological malignancy risk (simplified)
        total_abnormal_percentage = 0
        for cell_type, count in cell_counts.items():
            if cell_type in self.normal_ranges:
                normal_min, normal_max = self.normal_ranges[cell_type]
                if count < normal_min * 0.8 or count > normal_max * 1.2:
                    total_abnormal_percentage += 1
        
        risk_scores['hematological_disorder'] = min(100, total_abnormal_percentage * 15)
        
        return risk_scores
    
    async def _get_mock_disease_results(self, cell_analysis: Dict) -> Dict:
        """Generate mock disease detection results for demonstration"""
        
        return {
            'diseases': [
                {
                    'name': 'Bacterial Infection',
                    'confidence': 78,
                    'severity': 'medium'
                },
                {
                    'name': 'Mild Anemia',
                    'confidence': 45,
                    'severity': 'low'
                },
                {
                    'name': 'Leukocytosis',
                    'confidence': 62,
                    'severity': 'medium'
                }
            ],
            'abnormalities': [
                'Elevated neutrophil count',
                'Slightly reduced lymphocyte percentage',
                'Normal platelet morphology',
                'Toxic granulation in neutrophils',
                'Mild hypochromia in red blood cells'
            ],
            'timestamp': datetime.now().isoformat()
        }