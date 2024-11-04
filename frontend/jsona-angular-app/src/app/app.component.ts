import { Component, OnInit } from '@angular/core';
import { CourseService } from './services/course.service';

@Component({
  selector: 'app-root',
  template: `<p>{{ data | json }}</p>`
})
export class AppComponent implements OnInit {
  data: any;

  constructor(private courseService: CourseService) {}

  ngOnInit() {
    this.courseService.getCourses().subscribe(
      (response) => (this.data = response),
      (error) => console.error('Error:', error)
    );
  }
}
