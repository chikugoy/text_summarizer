import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class SummariesService {
  constructor(
    // @InjectRepository(Summary)
    // private summariesRepository: Repository<Summary>,
  ) {}

  async findAll() {
    // return this.summariesRepository.find();
    return [];
  }

  async findOne(id: number) {
    // return this.summariesRepository.findOne({ where: { id } });
    return { id };
  }

  async create(createSummaryDto: any) {
    // const summary = this.summariesRepository.create(createSummaryDto);
    // return this.summariesRepository.save(summary);
    return createSummaryDto;
  }

  async update(id: number, updateSummaryDto: any) {
    // await this.summariesRepository.update(id, updateSummaryDto);
    // return this.findOne(id);
    return { id, ...updateSummaryDto };
  }

  async remove(id: number) {
    // const summary = await this.findOne(id);
    // await this.summariesRepository.remove(summary);
    // return summary;
    return { id };
  }
}
