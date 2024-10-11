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
  filteredCourseList: Course[] = [];
  coursesService: CoursesService = inject(CoursesService);

  constructor() {
    this.coursesService.getAllCourses().then((courseList: Course[]) => {
      this.courseList = courseList;
      this.filteredCourseList = this.courseList;
      }
    )
  }

  filterResults(text: string) {
    if (!text) {
      this.filteredCourseList = this.courseList;
      return;
    }

    this.filteredCourseList = this.courseList.filter((course) =>
      course?.course_name.toLowerCase().includes(text.toLowerCase()),
    );

  }
}
