import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { CoursesService } from '../courses.service';
import { Course } from '../course';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';

@Component({
  selector: 'app-details',
  standalone: true,
  imports: [ CommonModule, ReactiveFormsModule ],
  templateUrl: './details.component.html',
  styleUrl: './details.component.css'
})
export class DetailsComponent {
  route: ActivatedRoute = inject(ActivatedRoute);
  coursesService = inject(CoursesService);
  course: Course | undefined ;
  applyForm = new FormGroup( {
    name: new FormControl(''),
    description: new FormControl('',)
  });

  constructor() {
    const courseId = this.route.snapshot.params['id'];
    this.coursesService.getCourseById(courseId).then((course) => {
      this.course = course;
    });
  }
  submitCourse() {
    this.coursesService.submitCourse(
      this.applyForm.value.name ?? '',
      this.applyForm.value.description ?? '',
    );
  }
}
