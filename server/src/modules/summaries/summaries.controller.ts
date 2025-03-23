import { Controller, Get, Post, Body, Param, Delete, Put } from '@nestjs/common';
import { SummariesService } from './summaries.service';

@Controller('summaries')
export class SummariesController {
  constructor(private readonly summariesService: SummariesService) {}

  @Get()
  findAll() {
    return this.summariesService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.summariesService.findOne(+id);
  }

  @Post()
  create(@Body() createSummaryDto: any) {
    return this.summariesService.create(createSummaryDto);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateSummaryDto: any) {
    return this.summariesService.update(+id, updateSummaryDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.summariesService.remove(+id);
  }
}
