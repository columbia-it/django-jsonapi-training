import { Injectable } from '@angular/core';
import { Course } from './course';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {

  constructor() {
  }

  protected courseList: Course[] = [
    {
      'id': '06d57ab7-087e-46fd-9131-853fe7739f32',
      'course_name': 'THE BODY AND SOCIETY',
      'course_description': 'THE BODY AND SOCIETY',
      'course_identifier': 'ANTH3160V',
      'course_number': '04961',
      'subject_area_code': 'ANTB',
      'suffix_two': '00',
      'school_bulletin_prefix_code': 'XCEFK9',
    },
    {
      'id': '31786aff-a593-46ca-8748-6e2c78107739',
      'course_name': 'METHODS/PROB OF PHILOS THOUGHT',
      'course_description': 'METHODS/PROB OF PHILOS THOUGHT',
      'course_identifier': 'AUPH1010O',
      'course_number': '87448',
      'subject_area_code': 'AUDT',
      'suffix_two': '00',
      'school_bulletin_prefix_code': 'O',
    },
  ];

  getAllCourses(): Course[] {
    return this.courseList;
  }

  getCourseById(id: string): Course | undefined {
    return this.courseList.find((course) => course.id === id);
  }
}
