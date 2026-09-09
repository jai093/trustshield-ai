/**
 * API request/response types
 */

import { ExtractedEmail, RiskAnalysis } from "./index";

export interface AnalyzeEmailRequest {
  email: ExtractedEmail;
  includeBackendAnalysis?: boolean;
  userContext?: Record<string, any>;
}

export interface AnalyzeEmailResponse {
  success: boolean;
  data?: RiskAnalysis;
  error?: string;
  processingTimeMs: number;
}

export interface ReportPhishingRequest {
  emailId: string;
  email: ExtractedEmail;
  riskAnalysis: RiskAnalysis;
  userReport?: string;
  reportType: "PHISHING" | "SPAM" | "FALSE_POSITIVE";
}

export interface ReportPhishingResponse {
  success: boolean;
  reportId: string;
  message: string;
}

export interface DashboardStats {
  totalEmailsAnalyzed: number;
  totalPhishingDetected: number;
  totalBlocked: number;
  detectionRate: number;
  topThreats: Array<{ threat: string; count: number }>;
  topBrands: Array<{ brand: string; count: number }>;
}

export interface BlockedEmailRecord {
  id: string;
  sender: string;
  subject: string;
  riskScore: number;
  threatCategory: string;
  action: string;
  blockedAt: string;
  details: RiskAnalysis;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: "Bearer";
}

export interface UserConfig {
  extensionVersion: string;
  apiEndpoint: string;
  enableBackendAnalysis: boolean;
  riskThreshold: number;
  enableQRBlocking: boolean;
  enableLinkDisabling: boolean;
  privacyMode: boolean;
  aiProvider: "local" | "openai" | "gemini" | "claude";
}
