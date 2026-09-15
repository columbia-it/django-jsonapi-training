export interface CommonAttributes {
  effective_start_date: string | null;
  effective_end_date: string | null;
  last_mod_user_name: string | null;
  last_mod_date: string;
  [key: string]: unknown;
}
export interface CourseAttributes extends CommonAttributes {
  school_bulletin_prefix_code: string;
  suffix_two: string;
  subject_area_code: string;
  course_number: string;
  course_identifier: string;
  course_name: string;
  course_description: string;
}
export interface PersonAttributes extends CommonAttributes {
  name: string;
}
export interface InstructorAttributes extends CommonAttributes {}
export interface CourseTermAttributes extends CommonAttributes {
  term_identifier: string;
  audit_permitted_code: number;
  exam_credit_flag: boolean;
}
export type ResourceName = 'courses' | 'course_terms' | 'instructors' | 'people';
export interface ResourceAttributesMap {
  courses: CourseAttributes;
  course_terms: CourseTermAttributes;
  instructors: InstructorAttributes;
  people: PersonAttributes;
}
