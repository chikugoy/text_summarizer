import { Controller, Post, Body, UploadedFile, UseInterceptors } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { OcrService } from './ocr.service';

@Controller('ocr')
export class OcrController {
  constructor(private readonly ocrService: OcrService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  processImage(@UploadedFile() file: Express.Multer.File, @Body() ocrRequestDto: any) {
    return this.ocrService.processImage(file, ocrRequestDto);
  }
}
