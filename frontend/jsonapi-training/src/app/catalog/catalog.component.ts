import { Component, inject } from '@angular/core';
import {CommonModule} from '@angular/common';
import { CourseComponent } from '../course/course.component';
import { Course } from '../course';
import { CoursesService } from '../courses.service';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, CourseComponent],
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.css'],
})
export class CatalogComponent {
  title = 'catalog';
  courseList: Course[] = [];
  coursesService: CoursesService = inject(CoursesService);

  constructor() {
    this.courseList = this.coursesService.getAllCourses();
  }

}
