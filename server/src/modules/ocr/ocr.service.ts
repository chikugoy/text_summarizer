import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class OcrService {
  private readonly logger = new Logger(OcrService.name);
  private readonly uploadDir: string;

  constructor(private configService: ConfigService) {
    this.uploadDir = this.configService.get<string>('UPLOAD_DEST') || './uploads';
    
    // アップロードディレクトリが存在しない場合は作成
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  async processImage(file: Express.Multer.File, ocrRequestDto: any) {
    try {
      this.logger.log(`Processing image: ${file?.originalname}`);
      
      // ファイルが存在しない場合はエラー
      if (!file) {
        throw new Error('ファイルが提供されていません');
      }

      // ファイルを保存
      const filePath = this.saveFile(file);
      
      // PaddleOCRを使用してテキスト抽出
      // 注意: 実際の実装では、PaddleOCRのPythonスクリプトを実行するか、
      // PaddleOCRのREST APIを使用する必要があります
      // 現時点では、サンプルテキストを返します
      
      // 実際の実装例（Pythonスクリプトを実行する場合）:
      // const { stdout } = await execPromise(`python3 paddleocr_script.py --image ${filePath}`);
      // const extractedText = stdout.trim();
      
      const extractedText = `PaddleOCRによる文章抽出のサンプルテキスト
これは実際の実装ではPaddleOCRを使用して抽出されたテキストが入ります。
現在はサンプルテキストを返しています。`;

      return {
        success: true,
        text: extractedText,
        file: {
          filename: file.originalname,
          path: filePath,
          mimetype: file.mimetype,
          size: file.size,
        },
        ...ocrRequestDto,
      };
    } catch (error: any) {
      this.logger.error(`OCR処理中にエラーが発生しました: ${error.message || '不明なエラー'}`);
      throw error;
    }
  }

  private saveFile(file: Express.Multer.File): string {
    // ファイル名が重複しないようにタイムスタンプを追加
    const timestamp = new Date().getTime();
    const filename = `${timestamp}-${file.originalname}`;
    const filePath = path.join(this.uploadDir, filename);
    
    // バッファからファイルを作成
    fs.writeFileSync(filePath, file.buffer);
    
    return filePath;
  }
}
