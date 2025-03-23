import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class ImagesService {
  constructor(
    // @InjectRepository(Image)
    // private imagesRepository: Repository<Image>,
  ) {}

  async findAll() {
    // return this.imagesRepository.find();
    return [];
  }

  async findOne(id: number) {
    // return this.imagesRepository.findOne({ where: { id } });
    return { id };
  }

  async create(file: Express.Multer.File, createImageDto: any) {
    // const image = this.imagesRepository.create({
    //   ...createImageDto,
    //   filename: file.filename,
    //   path: file.path,
    //   mimetype: file.mimetype,
    //   size: file.size,
    // });
    // return this.imagesRepository.save(image);
    return {
      ...createImageDto,
      filename: file?.filename,
      path: file?.path,
      mimetype: file?.mimetype,
      size: file?.size,
    };
  }

  async remove(id: number) {
    // const image = await this.findOne(id);
    // await this.imagesRepository.remove(image);
    // return image;
    return { id };
  }
}
