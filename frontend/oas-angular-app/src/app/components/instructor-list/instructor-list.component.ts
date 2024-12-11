import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { Router } from '@angular/router';
import { InstructorsService } from '../../core/api/v1';
@Component({
  selector: 'app-instructor-list',
  templateUrl: './instructor-list.component.html',
  styleUrl: './instructor-list.component.css'
})
export class InstructorListComponent implements OnInit, AfterViewInit {
  @ViewChild(MatPaginator, {static: false}) paginator!: MatPaginator;
  @ViewChild('tableContainer') tableContainer!: ElementRef; // Access table container for scrolling

  instructors: any | null = null;
  people: any | null = null;
  computedTerms: { [courseId: string]: any[] } = {}; // Precomputed terms for each instructor
  computedPeople: { [personId: string]: any[] } = {}; // Precompute person for each instructor
  searchFilter: string = '';
  displayedColumns: string[] = ['name', 'terms'];
  pageSize: number = 10; // Default page size
  pageNumber: number = 1; // Default page number
  scrollTop: number = 0; // Scroll position

  constructor(
    private instructorsService: InstructorsService,
    private router: Router
  ) {}

  ngOnInit() {
    const savedState = sessionStorage.getItem('instructorListState');
    if (savedState) {
      const {pageNumber, pageSize, scrollTop} = JSON.parse(savedState);
      this.pageNumber = pageNumber || 1;
      this.pageSize = pageSize || 10;
      this.scrollTop = scrollTop || 0;
    }

    this.loadInstructors();
  }

  ngAfterViewInit() {
    // Ensure paginator is initialized before synchronization
    if (this.paginator) {
      this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
      this.paginator.pageSize = this.pageSize;
    } else {
      console.error('instructor Paginator is not initialized');
    }
    // restore scroll position
    if (this.tableContainer) {
      this.tableContainer.nativeElement.scrollTop = this.scrollTop || 0; // Restore scroll position
    } else {
      console.error('instructor no tableContainer');
    }
  }

  loadInstructors() {
    this.instructorsService.instructorsList({
      fieldsInstructors: ['person', 'course_terms'],
      include: ['course_terms', 'person'],
      ...(this.searchFilter.trim() && { filterSearch: this.searchFilter }),
      pageNumber: this.pageNumber,
      pageSize: this.pageSize
    }).subscribe({
      next: (instructors) => {
        this.instructors = instructors;
        // precompute for each instructor: person and course_terms
        if (this.instructors?.data && this.instructors?.included) {
          this.instructors.data.forEach((instructor: any) => {
            const termIds = instructor.relationships?.course_terms?.data.map((term: any) => term.id) || [];
            const personId = instructor.relationships?.person?.data.id || null;
            this.computedTerms[instructor.id] = this.instructors.included.filter((included: any) =>
              termIds.includes(included.id)
            );
            this.computedPeople[instructor.id] = this.instructors.included.filter((included: any) =>
              personId.includes(included.id)
            );
          });
        }
        // Update paginator after instructors are loaded
        if (this.paginator) {
          this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
          this.paginator.pageSize = this.pageSize;
        } else {
          console.error('Paginator not available after loading instructor');
        }
      },
      error: (err) => console.error('Error:', err)
    });
  }
  onSearchFilterChange() {
    this.pageNumber = 1; // Reset to first page on new search
    this.loadInstructors();
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
    this.loadInstructors();
  }

  getTermsForInstructor(instructor: any): any[] {
    return this.computedTerms[instructor.id] || [];
  }
  getPeopleForInstructor(instructor: any): any[] {
    return this.computedPeople[instructor.id] || [];
  }

  onCourseClick(courseId: string) {
    sessionStorage.setItem(
      'instructorListState',
      JSON.stringify({
        pageNumber: this.paginator?.pageIndex + 1,
        pageSize: this.paginator?.pageSize,
        scrollTop: this.tableContainer?.nativeElement.scrollTop
      }));
  }
}
