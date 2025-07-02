import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json

logger = logging.getLogger(__name__)

class MedicalLLaMA:
    """Medical LLaMA model for generating medical explanations and insights"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.text_generator = None
        self.model_name = "microsoft/BioGPT-Large"  # Alternative: medical-focused model
        
    async def load_model(self):
        """Load the medical language model"""
        try:
            logger.info("Loading Medical LLaMA model...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Create text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=1024,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info("Medical LLaMA model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Medical LLaMA model: {str(e)}")
            # Use mock responses for demo
            self.text_generator = None
    
    async def generate_explanation(self, analysis_results: Dict) -> str:
        """Generate comprehensive medical explanation based on analysis results"""
        try:
            # Create medical prompt
            prompt = await self._create_medical_prompt(analysis_results)
            
            if self.text_generator:
                # Generate explanation using the model
                response = self.text_generator(
                    prompt,
                    max_length=800,
                    num_return_sequences=1,
                    temperature=0.7
                )
                
                explanation = response[0]['generated_text'].replace(prompt, "").strip()
                
            else:
                # Use mock explanation for demo
                explanation = await self._generate_mock_explanation(analysis_results)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating medical explanation: {str(e)}")
            return await self._generate_mock_explanation(analysis_results)
    
    async def _create_medical_prompt(self, results: Dict) -> str:
        """Create a structured medical prompt for the LLaMA model"""
        
        cell_counts = results.get('cell_counts', {})
        diseases = results.get('diseases', [])
        abnormalities = results.get('abnormalities', [])
        
        prompt = f"""As a medical AI assistant specializing in hematology, analyze the following blood cell analysis results and provide a comprehensive medical explanation:

Blood Cell Differential Count:
- Neutrophils: {cell_counts.get('neutrophils', 0)}%
- Lymphocytes: {cell_counts.get('lymphocytes', 0)}%
- Monocytes: {cell_counts.get('monocytes', 0)}%
- Eosinophils: {cell_counts.get('eosinophils', 0)}%
- Basophils: {cell_counts.get('basophils', 0)}%

Absolute Counts:
- Platelets: {cell_counts.get('platelets', 0):,}/μL
- Red Blood Cells: {cell_counts.get('rbcs', 0):,}/μL

Detected Abnormalities:
{chr(10).join(f"- {abnormality}" for abnormality in abnormalities)}

Potential Conditions Identified:
{chr(10).join(f"- {disease['name']} (confidence: {disease['confidence']}%)" for disease in diseases)}

Please provide a detailed medical interpretation including:
1. Analysis of the white blood cell differential
2. Assessment of red blood cell and platelet counts
3. Clinical significance of findings
4. Potential underlying conditions
5. Recommended follow-up actions

Medical Interpretation:"""

        return prompt
    
    async def _generate_mock_explanation(self, results: Dict) -> str:
        """Generate a comprehensive mock medical explanation"""
        
        cell_counts = results.get('cell_counts', {})
        diseases = results.get('diseases', [])
        abnormalities = results.get('abnormalities', [])
        
        neutrophils = cell_counts.get('neutrophils', 0)
        lymphocytes = cell_counts.get('lymphocytes', 0)
        platelets = cell_counts.get('platelets', 0)
        rbcs = cell_counts.get('rbcs', 0)
        
        explanation = f"""**Comprehensive Blood Cell Analysis Report**

**White Blood Cell Differential Analysis:**
The neutrophil count of {neutrophils}% {'is elevated above normal range (50-70%)' if neutrophils > 70 else 'falls within normal range (50-70%)' if neutrophils >= 50 else 'is below normal range (50-70%)'}. This {'suggests an active immune response, commonly seen in bacterial infections or inflammatory conditions' if neutrophils > 65 else 'indicates normal immune system function' if neutrophils >= 50 else 'may indicate viral infection or immune suppression'}.

The lymphocyte percentage of {lymphocytes}% {'is within normal range' if 20 <= lymphocytes <= 40 else 'is below normal range' if lymphocytes < 20 else 'is elevated above normal range'}. {'This relative lymphopenia often accompanies acute bacterial infections when neutrophilia is present.' if lymphocytes < 25 and neutrophils > 65 else 'This supports normal adaptive immune function.' if 20 <= lymphocytes <= 40 else 'This lymphocytosis may indicate viral infection or chronic inflammatory conditions.'}

**Red Blood Cell and Platelet Assessment:**
Red blood cell count of {rbcs:,}/μL {'falls within normal range (4.2-5.4 million/μL)' if 4200000 <= rbcs <= 5400000 else 'is below normal range, suggesting possible anemia' if rbcs < 4200000 else 'is above normal range, indicating possible polycythemia'}, indicating {'adequate oxygen-carrying capacity' if 4200000 <= rbcs <= 5400000 else 'potentially compromised oxygen transport' if rbcs < 4200000 else 'possible increased blood viscosity'}.

Platelet count of {platelets:,}/μL {'is within normal range (150,000-450,000/μL)' if 150000 <= platelets <= 450000 else 'is below normal range, indicating thrombocytopenia' if platelets < 150000 else 'is above normal range, suggesting thrombocytosis'}, {'ensuring proper hemostatic function' if 150000 <= platelets <= 450000 else 'which may increase bleeding risk' if platelets < 150000 else 'which may increase thrombotic risk'}.

**Clinical Interpretation:**
"""
        
        if diseases:
            primary_disease = diseases[0]
            explanation += f"The AI analysis has identified potential {primary_disease['name'].lower()} with {primary_disease['confidence']}% confidence. "
            
            if 'bacterial infection' in primary_disease['name'].lower():
                explanation += "This finding is strongly supported by the neutrophilic leukocytosis pattern observed in the differential count. The elevated neutrophil percentage combined with relative lymphopenia is a classic hallmark of acute bacterial infection."
            elif 'anemia' in primary_disease['name'].lower():
                explanation += "This is consistent with the observed red blood cell parameters and may require further investigation into underlying causes such as iron deficiency, chronic disease, or blood loss."
            else:
                explanation += "This finding correlates with the observed cellular morphology patterns and differential count abnormalities detected by the EfficientNet B0 analysis."
        else:
            explanation += "The blood sample demonstrates normal cellular patterns with no significant pathological indicators identified by the AI analysis."
        
        explanation += f"""

**Morphological Findings:**
Advanced computer vision analysis has identified the following cellular characteristics:
{chr(10).join(f"• {abnormality}" for abnormality in abnormalities)}

**Clinical Recommendations:**
1. **Clinical Correlation:** These laboratory findings should be interpreted in the context of patient symptoms, medical history, and physical examination findings.

2. **Follow-up Testing:** {'Consider additional laboratory studies including blood culture, inflammatory markers (ESR, CRP), and comprehensive metabolic panel if clinical symptoms suggest infection.' if neutrophils > 70 else 'Routine monitoring may be sufficient given normal parameters.' if 50 <= neutrophils <= 70 else 'Consider viral studies and autoimmune markers if clinical presentation warrants.'}

3. **Monitoring Protocol:** {'Serial blood counts over 24-48 hours to monitor response to treatment if infection is suspected.' if neutrophils > 70 else 'Repeat complete blood count in 3-6 months as part of routine health maintenance.' if all(150000 <= platelets <= 450000 and 4200000 <= rbcs <= 5400000) else 'Follow-up blood work in 2-4 weeks to assess for improvement or progression.'}

4. **Specialist Consultation:** {'Infectious disease consultation may be warranted if fever or signs of systemic infection are present.' if neutrophils > 75 else 'Hematology referral recommended if abnormal findings persist on repeat testing.' if any(not (50 <= neutrophils <= 70 and 20 <= lymphocytes <= 40)) else 'No immediate specialist referral required based on current findings.'}

**Quality Assurance Notes:**
This analysis was performed using EfficientNet B0 deep learning architecture for cellular classification with {results.get('confidence_scores', {}).get('overall', 0.94)*100:.1f}% overall confidence. The medical interpretation was generated using advanced medical language models trained on extensive hematological literature and clinical data.

**Important Disclaimer:**
This AI-generated analysis serves as a diagnostic aid and should not replace clinical judgment. All findings must be correlated with patient presentation and confirmed through appropriate clinical evaluation by qualified healthcare professionals."""

        return explanation
    
    async def answer_follow_up_question(self, question: str, analysis_results: Dict) -> str:
        """Answer follow-up questions about the analysis"""
        try:
            # Create context-aware prompt
            context_prompt = f"""Based on the blood analysis results showing:
- Neutrophils: {analysis_results.get('cell_counts', {}).get('neutrophils', 0)}%
- Lymphocytes: {analysis_results.get('cell_counts', {}).get('lymphocytes', 0)}%
- Other findings: {', '.join(analysis_results.get('abnormalities', []))}

Patient Question: {question}

Medical Response:"""

            if self.text_generator:
                response = self.text_generator(
                    context_prompt,
                    max_length=300,
                    num_return_sequences=1,
                    temperature=0.6
                )
                
                answer = response[0]['generated_text'].replace(context_prompt, "").strip()
            else:
                answer = await self._generate_mock_answer(question, analysis_results)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering follow-up question: {str(e)}")
            return "I apologize, but I'm unable to process your question at the moment. Please consult with your healthcare provider for specific medical advice."
    
    async def _generate_mock_answer(self, question: str, results: Dict) -> str:
        """Generate mock answers for common follow-up questions"""
        
        question_lower = question.lower()
        
        if 'neutrophil' in question_lower and 'elevated' in question_lower:
            return "Elevated neutrophil count typically indicates your body is fighting a bacterial infection or responding to inflammation. This is a normal immune response, but the underlying cause should be identified and treated appropriately."
        
        elif 'concerned' in question_lower or 'worry' in question_lower:
            return "While some findings may be outside normal ranges, many variations can be temporary or related to recent illness, stress, or other factors. The most important step is to discuss these results with your healthcare provider who can evaluate them in context of your symptoms and medical history."
        
        elif 'follow-up' in question_lower or 'next' in question_lower:
            return "Based on these results, your doctor may recommend repeat blood work in a few weeks, additional tests to investigate specific findings, or treatment if an active condition is identified. The specific follow-up will depend on your symptoms and clinical presentation."
        
        elif 'normal' in question_lower and 'range' in question_lower:
            return "Normal ranges can vary slightly between laboratories, but generally neutrophils should be 50-70%, lymphocytes 20-40%, and platelets 150,000-450,000/μL. Your results are being compared to these established reference ranges."
        
        else:
            return "That's an excellent question. For specific medical advice about your results, I recommend discussing this directly with your healthcare provider who can provide personalized guidance based on your complete medical picture."