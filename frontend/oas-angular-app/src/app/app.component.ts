import { Component, OnInit } from '@angular/core';
import { CoursesService, Course } from './core/api/v1';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  data: any;

  constructor(private coursesService: CoursesService) {
  }

  ngOnInit() {
    // I think this is vestigial code
    this.coursesService.coursesList().subscribe(
      (response) => (this.data = response),
      (error) => console.error('Error:', error)
    );
    console.log(this.data)
  }
}
