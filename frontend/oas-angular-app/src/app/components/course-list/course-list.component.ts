import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { Router } from '@angular/router';
import { CoursesService } from '../../core/api/v1';

@Component({
    selector: 'app-course-list',
    templateUrl: './course-list.component.html',
    styleUrl: './course-list.component.css',
    standalone: false
})
export class CourseListComponent implements OnInit, AfterViewInit {
  @ViewChild(MatPaginator, { static: false }) paginator!: MatPaginator;
  @ViewChild('tableContainer') tableContainer!: ElementRef; // Access table container for scrolling

  courses: any | null = null;
  computedTerms: { [courseId: string]: any[] } = {}; // Precomputed terms for each course
  searchFilter: string = '';
  displayedColumns: string[] = ['identifier', 'name', 'description', 'terms']; // Columns to display in the table
  pageSize: number = 10; // Default page size
  pageNumber: number = 1; // Default page number
  scrollTop: number = 0; // Scroll position
  constructor(private coursesService: CoursesService, private router: Router) {}

  ngOnInit() {
    const savedState = sessionStorage.getItem('courseListState');
    if (savedState) {
      const {pageNumber, pageSize, scrollTop} = JSON.parse(savedState);
      this.pageNumber = pageNumber || 1;
      this.pageSize = pageSize || 10;
      this.scrollTop = scrollTop || 0;
    }

    this.loadCourses();
  }
  ngAfterViewInit() {
    // Ensure paginator is initialized before synchronization
    if (this.paginator) {
      this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
      this.paginator.pageSize = this.pageSize;
    } else {
      console.error('course Paginator is not initialized');
    }
    // restore scroll position
    if (this.tableContainer) {
      this.tableContainer.nativeElement.scrollTop = this.scrollTop || 0; // Restore scroll position
    } else {
      console.error('course no tableContainer');
    }
  }
  loadCourses() {
    // only get the fields we care to display
    this.coursesService.coursesList({
      fieldsCourses: ["course_identifier", "course_name", "course_description", "course_terms"],
      include: ["course_terms"],
      ...(this.searchFilter.trim() && { filterSearch: this.searchFilter }),
      pageNumber: this.pageNumber,
      pageSize: this.pageSize
    }).subscribe({
      next: (courses) => {
        this.courses = courses;

        // Precompute terms for each course
        if (this.courses?.data && this.courses?.included) {
          this.courses.data.forEach((course: any) => {
            const termIds = course.relationships?.course_terms?.data.map((term: any) => term.id) || [];
            this.computedTerms[course.id] = this.courses.included.filter((included: any) =>
              termIds.includes(included.id)
            );
          });
        }

      // Update paginator after courses are loaded
        if (this.paginator) {
          this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
          this.paginator.pageSize = this.pageSize;
        } else {
          console.error('Paginator not available after loading courses');
        }
      },
      error: (err) => console.error('Error:', err)
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
  onPageChange(event: any) {
    this.pageSize = event.pageSize;
    this.pageNumber = event.pageIndex + 1; // pageIndex is 0-based, so add 1
    this.loadCourses();
  }

  onCourseClick(courseId: string) {
    // Save current state before navigation
    sessionStorage.setItem(
      'courseListState',
      JSON.stringify({
        pageNumber: this.paginator?.pageIndex + 1,
        pageSize: this.paginator?.pageSize,
        scrollTop: this.tableContainer?.nativeElement.scrollTop
      })
    );
  }

 /**
   * Retrieve precomputed terms for a course.
   */
  getTermsForCourse(course: any): any[] {
    return this.computedTerms[course.id] || [];
  }
}
