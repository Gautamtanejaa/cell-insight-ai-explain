import cv2
import numpy as np
import asyncio
from typing import Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Image preprocessing service for blood smear analysis"""
    
    def __init__(self):
        self.target_size = (1024, 1024)
        self.min_size = (256, 256)
        
    async def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess blood smear image for analysis"""
        try:
            logger.info(f"Preprocessing image: {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Validate image quality
            await self._validate_image_quality(image)
            
            # Color space conversion and normalization
            processed_image = await self._normalize_colors(image)
            
            # Resize image
            processed_image = await self._resize_image(processed_image)
            
            # Enhance contrast and remove artifacts
            processed_image = await self._enhance_image(processed_image)
            
            # Apply noise reduction
            processed_image = await self._reduce_noise(processed_image)
            
            logger.info("Image preprocessing completed successfully")
            return processed_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    async def _validate_image_quality(self, image: np.ndarray) -> None:
        """Validate if image meets quality requirements for analysis"""
        
        height, width = image.shape[:2]
        
        # Check minimum resolution
        if height < self.min_size[0] or width < self.min_size[1]:
            raise ValueError(f"Image resolution too low: {width}x{height}. Minimum required: {self.min_size[0]}x{self.min_size[1]}")
        
        # Check if image is too dark or too bright
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness < 30:
            raise ValueError("Image is too dark for analysis")
        elif mean_brightness > 220:
            raise ValueError("Image is too bright/overexposed for analysis")
        
        # Check for blur using Laplacian variance
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100:
            logger.warning(f"Image appears blurry (blur score: {blur_score:.2f})")
        
        logger.info(f"Image quality validation passed - Resolution: {width}x{height}, Brightness: {mean_brightness:.1f}, Blur score: {blur_score:.2f}")
    
    async def _normalize_colors(self, image: np.ndarray) -> np.ndarray:
        """Normalize colors for consistent analysis"""
        
        # Convert to LAB color space for better color normalization
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels back
        lab = cv2.merge([l, a, b])
        
        # Convert back to BGR
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return normalized
    
    async def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image to target size while maintaining aspect ratio"""
        
        height, width = image.shape[:2]
        target_width, target_height = self.target_size
        
        # Calculate scaling factor to maintain aspect ratio
        scale_x = target_width / width
        scale_y = target_height / height
        scale = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center the image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # Calculate position to center the image
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
        
        return canvas
    
    async def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast and remove artifacts"""
        
        # Convert to YUV for better processing
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        
        # Apply histogram equalization to Y channel
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        
        # Apply sharpening filter
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Blend original and sharpened image
        result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)
        
        return result
    
    async def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Apply noise reduction while preserving cell details"""
        
        # Apply Non-local Means Denoising
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # Apply bilateral filter for edge-preserving smoothing
        bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        return bilateral
    
    async def extract_roi(self, image: np.ndarray, roi_coords: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract region of interest from image"""
        
        x, y, width, height = roi_coords
        
        # Validate coordinates
        img_height, img_width = image.shape[:2]
        
        x = max(0, min(x, img_width))
        y = max(0, min(y, img_height))
        width = min(width, img_width - x)
        height = min(height, img_height - y)
        
        # Extract ROI
        roi = image[y:y + height, x:x + width]
        
        return roi
    
    async def create_overlay(self, image: np.ndarray, detections: list) -> np.ndarray:
        """Create overlay with detected cells highlighted"""
        
        overlay = image.copy()
        
        for detection in detections:
            cell_type = detection.get('type', 'unknown')
            confidence = detection.get('confidence', 0.0)
            bbox = detection.get('bbox', [0, 0, 0, 0])
            
            x, y, w, h = bbox
            
            # Color mapping for different cell types
            color_map = {
                'neutrophil': (0, 255, 0),      # Green
                'lymphocyte': (255, 0, 0),      # Blue
                'monocyte': (0, 255, 255),      # Yellow
                'eosinophil': (255, 0, 255),    # Magenta
                'basophil': (0, 0, 255),        # Red
                'platelet': (255, 255, 0),      # Cyan
                'rbc': (128, 128, 128)          # Gray
            }
            
            color = color_map.get(cell_type.lower(), (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{cell_type}: {confidence:.2f}"
            cv2.putText(overlay, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return overlay