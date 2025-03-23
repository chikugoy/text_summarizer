import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ConfigService } from '@nestjs/config';
import { Summary } from './entities/summary.entity';
import { ChatOpenAI } from '@langchain/openai';
import { PromptTemplate } from '@langchain/core/prompts';
import { LLMChain } from 'langchain/chains';

@Injectable()
export class SummariesService {
  private readonly logger = new Logger(SummariesService.name);
  private readonly llm: ChatOpenAI;
  private readonly summaryPrompt: PromptTemplate;

  constructor(
    @InjectRepository(Summary)
    private summariesRepository: Repository<Summary>,
    private configService: ConfigService
  ) {
    // LangChainの初期化
    const apiKey = this.configService.get<string>('OPENAI_API_KEY');
    const model = this.configService.get<string>('OPENAI_MODEL') || 'gpt-3.5-turbo';
    
    this.llm = new ChatOpenAI({
      openAIApiKey: apiKey,
      modelName: model,
      temperature: 0.3,
    });

    // 要約用のプロンプトテンプレート
    this.summaryPrompt = PromptTemplate.fromTemplate(
      `以下の文章を要約してください。重要なポイントを保持しながら、簡潔にまとめてください。

文章:
{text}

要約:`
    );
  }

  async findAll() {
    this.logger.log('全ての要約を取得します');
    return this.summariesRepository.find({
      order: { createdAt: 'DESC' }
    });
  }

  async findOne(id: number) {
    this.logger.log(`ID: ${id} の要約を取得します`);
    const summary = await this.summariesRepository.findOne({ where: { id } });
    if (!summary) {
      throw new Error(`ID: ${id} の要約が見つかりません`);
    }
    return summary;
  }

  async create(createSummaryDto: any) {
    try {
      this.logger.log('新しい要約を作成します');
      
      // 入力テキストの取得
      const { text, title } = createSummaryDto;
      
      if (!text) {
        throw new Error('要約するテキストが提供されていません');
      }
      
      // LangChainを使用してテキストを要約
      const chain = new LLMChain({ llm: this.llm, prompt: this.summaryPrompt });
      const result = await chain.call({ text });
      const summarizedText = result.text || '要約を生成できませんでした';
      
      // 要約をデータベースに保存
      const summary = this.summariesRepository.create({
        title: title || '無題の要約',
        content: summarizedText,
        source: text,
      });
      
      return this.summariesRepository.save(summary);
    } catch (error: any) {
      this.logger.error(`要約作成中にエラーが発生しました: ${error.message || '不明なエラー'}`);
      throw error;
    }
  }

  async update(id: number, updateSummaryDto: any) {
    this.logger.log(`ID: ${id} の要約を更新します`);
    await this.summariesRepository.update(id, updateSummaryDto);
    return this.findOne(id);
  }

  async remove(id: number) {
    this.logger.log(`ID: ${id} の要約を削除します`);
    const summary = await this.findOne(id);
    await this.summariesRepository.remove(summary);
    return summary;
  }
}
