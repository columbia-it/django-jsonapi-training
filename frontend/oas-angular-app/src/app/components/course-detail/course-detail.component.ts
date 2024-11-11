import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CoursesService, Course } from '../../core/api/v1';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrl: './course-detail.component.css'
})
export class CourseDetailComponent implements OnInit {
  course: any;

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService
  ) {}

  ngOnInit() {
    const courseId = this.route.snapshot.paramMap.get('id');

    if (courseId) {
      this.coursesService.coursesRetrieve(courseId, [], ['course_terms']).subscribe(
	(course) => {
	  this.course = course;
	  console.log(this.course)
	},
	(error) => console.error('Error:', error)
      );
    }
  }
}
