import { Component, OnInit } from '@angular/core';
import { CoursesService } from '../../core/api/v1';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.css'
})
export class CourseListComponent implements OnInit {
  courses: any | null = null;
  searchFilter: string = '';
  displayedColumns: string[] = ['identifier', 'name', 'description']; // Columns to display in the table

  constructor(private coursesService: CoursesService) {}

  ngOnInit() {
    this.loadCourses();
  }

  loadCourses() {
    // only get the fields we care to display
    this.coursesService.coursesList({
      fieldsCourses: ["course_identifier", "course_name", "course_description"],
      filterSearch: this.searchFilter,
      pageSize: 20
    }).subscribe(
      (courses) => {
        this.courses = courses;
        console.log(this.courses)
      },
      (error) => console.error('Error:', error)
    );
  }
  onSearchFilterChange() {
    this.loadCourses();
  }
  clearSearch() {
    this.searchFilter = ''; // Reset the search filter
    this.loadCourses();     // Reload courses without filter
  }

}
