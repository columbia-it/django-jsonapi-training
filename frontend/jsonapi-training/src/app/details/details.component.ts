import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { CoursesService } from '../courses.service';
import { Course } from '../course';

@Component({
  selector: 'app-details',
  standalone: true,
  imports: [ CommonModule ],
  templateUrl: './details.component.html',
  styleUrl: './details.component.css'
})
export class DetailsComponent {
  route: ActivatedRoute = inject(ActivatedRoute);
  coursesService = inject(CoursesService);
  course: Course | undefined ;

  constructor() {
    const courseId = this.route.snapshot.params['id'];
    this.course = this.coursesService.getCourseById(courseId)
  }

}
