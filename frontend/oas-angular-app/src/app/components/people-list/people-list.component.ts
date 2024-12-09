import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { Router } from '@angular/router';
import { PeopleService, InstructorsService } from '../../core/api/v1';

@Component({
  selector: 'app-people-list',
  templateUrl: './people-list.component.html',
  styleUrl: './people-list.component.css'
})
export class PeopleListComponent implements OnInit, AfterViewInit {
  @ViewChild(MatPaginator, {static: false}) paginator!: MatPaginator;
  @ViewChild('tableContainer') tableContainer!: ElementRef; // Access table container for scrolling

  people: any | null = null;
  instructors: any | null = null;
  searchFilter: string = '';
  displayedColumns: string[] = ['name','isInstructor'];
  pageSize: number = 10; // Default page size
  pageNumber: number = 1; // Default page number
  scrollTop: number = 0; // Scroll position

  constructor(
    private peopleService: PeopleService,
    private instructorsService: InstructorsService,
    private router: Router
  ) {}

    ngOnInit() {
    const savedState = sessionStorage.getItem('peopleListState');
    if (savedState) {
      const {pageNumber, pageSize, scrollTop} = JSON.parse(savedState);
      this.pageNumber = pageNumber || 1;
      this.pageSize = pageSize || 10;
      this.scrollTop = scrollTop || 0;
    }

    this.loadPeople();
  }

  ngAfterViewInit() {
    // Ensure paginator is initialized before synchronization
    if (this.paginator) {
      console.log('people Paginator initialized');
      this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
      this.paginator.pageSize = this.pageSize;
    } else {
      console.error('people Paginator is not initialized');
    }
    // restore scroll position
    if (this.tableContainer) {
      console.log('people has tableContainer');
      this.tableContainer.nativeElement.scrollTop = this.scrollTop || 0; // Restore scroll position
    } else {
      console.error('people no tableContainer');
    }
  }

  loadPeople() {
   this.peopleService.peopleList({
      fieldsPeople: ['name', 'instructor'],
      include: ['instructor'],
      ...(this.searchFilter.trim() && { filterSearch: this.searchFilter }),
      pageNumber: this.pageNumber,
      pageSize: this.pageSize
    }).subscribe({
      next: (people) => {
        this.people = people;
        console.log(this.people);
        // Update paginator after people are loaded
        if (this.paginator) {
          console.log('Synchronizing paginator');
          this.paginator.pageIndex = this.pageNumber - 1; // 1-based to 0-based
          this.paginator.pageSize = this.pageSize;
        } else {
          console.error('Paginator not available after loading people');
        }
      },
      error: (err) => console.error('Error:', err)
    });
    // search instructors for matching person.id
    for (let person of this.people.data) {
      console.log('person:', person);
    }

  }

  onSearchFilterChange() {
    this.pageNumber = 1; // Reset to first page on new search
    this.loadPeople();
    //this.loadIPeople();
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
    this.loadPeople();
    //this.loadIPeople();
  }

}
