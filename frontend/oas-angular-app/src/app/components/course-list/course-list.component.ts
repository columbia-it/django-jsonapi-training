import { Component, OnInit } from '@angular/core';
import { CoursesService, Course } from '../../core/api/v1';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.css'
})
export class CourseListComponent implements OnInit {
  courses: any;

  constructor(private coursesService: CoursesService) {}

  ngOnInit() {
    // only get the fields we care to display
    this.coursesService.coursesList(["course_identifier","course_name"]).subscribe(
      (courses) => {
	this.courses = courses;
	console.log(this.courses)	
      },
      (error) => console.error('Error:', error)
    );
  }
}
