import { Component, OnInit } from '@angular/core';
import { CoursesService } from '../../core/api/v1';
import { PageEvent } from '@angular/material/paginator';

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
  pageSize: number = 10; // Default page size
  pageNumber: number = 1; // Default page number
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
      pageNumber: this.pageNumber,
      pageSize: this.pageSize
    }).subscribe({
      next: (courses) => {
        this.courses = courses;

        // Precompute terms for each course
        if (this.courses?.data && this.courses?.included) {
          this.courses.data.forEach((course: any) => {
            const termIds = course.relationships?.course_terms?.data.map((term: any) => term.id) || [];
            this.computedTerms[course.id] = this.courses.included.filter((included: any) => termIds.includes(included.id));
          });
        }

        console.log(this.courses);
      },
      error: (err) => {
        console.error('Error:', err);
      },
      complete: () => {
        console.log('Courses loading complete');
      }
    });
  }
  onSearchFilterChange() {
    this.pageNumber = 1; // Reset to first page on new search
    this.loadCourses();
  }
  clearSearch() {
    this.searchFilter = ''; // Reset the search filter
    this.onSearchFilterChange();     // Reload courses without filter
  }
  /**
   * Handle page changes from the paginator.
   */
  onPageChange(event: PageEvent) {
    this.pageSize = event.pageSize;
    this.pageNumber = event.pageIndex + 1; // pageIndex is 0-based, so add 1
    this.loadCourses();
  }
 /**
   * Retrieve precomputed terms for a course.
   */
  getTermsForCourse(course: any): any[] {
    return this.computedTerms[course.id] || [];
  }
}
