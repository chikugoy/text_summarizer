import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHealth() {
    return {
      status: 'ok',
      message: 'Text Summarizer API is running',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
    };
  }
}
