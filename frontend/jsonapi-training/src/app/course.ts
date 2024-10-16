import { JsonApiModelConfig, JsonApiModel, Attribute, HasMany, BelongsTo } from 'angular2-jsonapi';

@JsonApiModelConfig({
    type: 'courses'
})
export class Course extends JsonApiModel {
  @Attribute()
  course_name: string;

  @Attribute()
  course_description: string;

  @Attribute()
  course_number: string;

  @Attribute()
  course_identifier: string;

  @Attribute()
  subject_area_code: string;

  @Attribute()
  suffix_two: string;

  @Attribute()
  school_bulletin_prefix_code: string;
}
