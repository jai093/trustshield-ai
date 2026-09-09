"""
AI Agents Module
Provides all AI analysis agents for phishing detection
"""

from email_extraction_agent import EmailExtractionAgent
from brand_verification_agent import BrandVerificationAgent
from intent_detection_agent import IntentDetectionAgent
from url_intelligence_agent import URLIntelligenceAgent
from psychology_manipulation_agent import PsychologyManipulationAgent
from qr_detection_agent import QRDetectionAgent
from attachment_analysis_agent import AttachmentAnalysisAgent
from decision_fusion_agent import DecisionFusionAgent

__all__ = [
    'EmailExtractionAgent',
    'BrandVerificationAgent',
    'IntentDetectionAgent',
    'URLIntelligenceAgent',
    'PsychologyManipulationAgent',
    'QRDetectionAgent',
    'AttachmentAnalysisAgent',
    'DecisionFusionAgent',
]
