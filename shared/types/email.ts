/**
 * Shared Email-related TypeScript types
 * Used across Chrome Extension, Backend, and Dashboard
 */

export interface EmailMetadata {
  sender: string;
  senderName?: string;
  senderDomain?: string;
  subject: string;
  replyTo?: string;
  timestamp: string;
  gmailMessageId?: string;
  threadId?: string;
}

export interface EmailContent {
  body: string;
  htmlBody?: string;
  plainText: string;
}

export interface ExtractedLink {
  text: string;
  href: string;
  visible: boolean;
  isButton?: boolean;
}

export interface ExtractedImage {
  src: string;
  alt?: string;
  width?: number;
  height?: number;
  dataUrl?: string;
}

export interface ExtractedAttachment {
  name: string;
  mimeType: string;
  size: number;
  extension: string;
  isExecutable?: boolean;
  hasMacros?: boolean;
}

export interface QRCode {
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  decodedValue?: string;
  destinationUrl?: string;
  imageData: string;
}

export interface ExtractedEmail {
  metadata: EmailMetadata;
  content: EmailContent;
  links: ExtractedLink[];
  images: ExtractedImage[];
  attachments: ExtractedAttachment[];
  qrCodes: QRCode[];
  htmlDom?: string;
  extractedAt: string;
}

export interface AnalysisRequest {
  email: ExtractedEmail;
  includeBackendAnalysis?: boolean;
  userProfile?: UserProfile;
}

export interface UserProfile {
  trustedContacts: string[];
  frequentDomains: string[];
  commonBanks: string[];
  frequentNewsletters: string[];
  trustedOrganizations: string[];
  personalWritingStyle?: string;
}
