import { Component, OnInit } from '@angular/core';
import { CoursesService } from '../../core/api/v1';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.css'
})
export class CourseListComponent implements OnInit {
  courses: any | null = null;
  computedTerms: { [courseId: string]: any[] } = {}; // Precomputed terms for each course
  searchFilter: string = '';
  displayedColumns: string[] = ['identifier', 'name', 'description', 'terms']; // Columns to display in the table

  constructor(private coursesService: CoursesService) {}

  ngOnInit() {
    this.loadCourses();
  }

  loadCourses() {
    // only get the fields we care to display
    this.coursesService.coursesList({
      fieldsCourses: ["course_identifier", "course_name", "course_description", "course_terms"],
      include: ["course_terms"],
      filterSearch: this.searchFilter,
      pageSize: 20 // TODO fix this & add pagination
    }).subscribe(
      (courses) => {
        this.courses = courses;
        // Precompute terms for each course
        if (this.courses?.data && this.courses?.included) {
          this.courses.data.forEach((course: any) => {
            const termIds = course.relationships?.course_terms?.data.map((term: any) => term.id) || [];
            this.computedTerms[course.id] = this.courses.included.filter((included: any) => termIds.includes(included.id));
          });
        }
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

 /**
   * Retrieve precomputed terms for a course.
   */
  getTermsForCourse(course: any): any[] {
    return this.computedTerms[course.id] || [];
  }
}
