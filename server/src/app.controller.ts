import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { AppService } from './app.service';

@ApiTags('app')
@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  @ApiOperation({ summary: 'ヘルスチェック' })
  @ApiResponse({ 
    status: 200, 
    description: 'APIサーバーが正常に動作していることを確認します',
    schema: {
      type: 'object',
      properties: {
        status: { type: 'string', example: 'ok' },
        message: { type: 'string', example: 'Text Summarizer API is running' },
        version: { type: 'string', example: '0.1.0' },
      }
    }
  })
  getHealth() {
    return this.appService.getHealth();
  }
}
