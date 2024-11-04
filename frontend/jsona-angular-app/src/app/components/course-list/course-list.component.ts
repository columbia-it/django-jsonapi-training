import { Component, OnInit } from '@angular/core';
import { CourseService } from '../../services/course.service';
import { Course } from '../../models/course.model';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html'
})
export class CourseListComponent implements OnInit {
  courses: Course[] = [];
  newCourse: Course = {
    id: '',
    course_identifier: '',
    course_name: '',
    course_description: '',
    course_number: '',
    school_bulletin_prefix_code: '',
    suffix_two: '',
    subject_area_code: ''
  };

  constructor(private courseService: CourseService) {}

  ngOnInit() {
    this.courseService.getCourses().subscribe((courses) => {
      this.courses = courses;
    });
  }

  addCourse() {
    this.courseService.createCourse(this.newCourse).subscribe((course) => {
      this.courses.push(course);
      this.newCourse = {
        id: '',
        course_identifier: '',
        course_name: '',
        course_description: '',
        course_number: '',
        school_bulletin_prefix_code: '',
        suffix_two: '',
        subject_area_code: ''
      };
    });
  }
}
