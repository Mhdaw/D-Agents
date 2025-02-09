import { Message as AiMessage } from 'ai';

export interface Message extends AiMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'data';
  content: string;
  createdAt: Date;
  chatId: string;
}

export interface Chat {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Vote {
  id: string;
  userId: string;
  messageId: string;
  chatId: string;
  value: 'up' | 'down';
  isUpvoted: boolean;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}
export interface Message extends AiMessage {
    chatId: string;
  }
  