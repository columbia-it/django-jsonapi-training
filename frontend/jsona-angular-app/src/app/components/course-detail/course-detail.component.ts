import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CourseService } from '../../services/course.service';
import { Course } from '../../models/course.model';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html'
})
export class CourseDetailComponent implements OnInit {
  course: Course | null = null;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService
  ) {}

  ngOnInit() {
    const courseId = this.route.snapshot.paramMap.get('id');
    if (courseId) {
      this.courseService.getCourse(courseId).subscribe(
        (course) => (this.course = course),
        (error) => console.error('Error fetching course:', error)
      );
    }
  }
}
