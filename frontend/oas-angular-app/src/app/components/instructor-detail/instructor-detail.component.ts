import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseTermsService, InstructorsService } from '../../core/api/v1';
// this is pretty duplicative of InstructorListComponent.
@Component({
  selector: 'app-instructor-detail',
  templateUrl: './instructor-detail.component.html',
  styleUrl: './instructor-detail.component.css'
})
export class InstructorDetailComponent implements OnInit {
  instructor: any;
  person: any;
  courseTerms:  { [key: string]: any } = {};
  origin: string | null = null;

constructor(
    private route: ActivatedRoute,
    private courseTermsService: CourseTermsService,
    private instructorsService: InstructorsService,
    private router: Router
  ) {}

ngOnInit() {
    const instructorId = this.route.snapshot.paramMap.get('id');
    this.origin = this.route.snapshot.queryParamMap.get('origin');
    console.log('instructor-detail init origin', this.route.snapshot.queryParams);

    if (instructorId) {
      this.instructorsService.instructorsRetrieve({
        id: instructorId,
        include: ['course_terms', 'person']
      }).subscribe({
        next: (instructor) => {
          this.instructor = instructor;
          console.log('instructor:', this.instructor);
          this.loadCourseTerms();
        },
        error: (error) => console.error('Error:', error)
      });
    }
  }
  goBack() {
    console.log('goBack origin:', this.origin);
    this.router.navigate([this.origin ? this.origin : '/home']);
  }

  // load courses associated with the CourseTerms.
  loadCourseTerms() {
    if (!this.instructor?.included) return;
    const courseTermIds = new Set(
      this.instructor.included
        .filter((item: any) => item.type === 'course_terms')  // Filter for course_terms
        .flatMap((term: any)  => term.id)
    );
    courseTermIds.forEach((id) => {
      const courseTermId = id as string;

      this.courseTermsService.courseTermsRetrieve({
        id: courseTermId,
        include: ['course']
      }).subscribe({
        next: (courseTerm) => (this.courseTerms[courseTermId] = courseTerm),
        error: (error) => console.error(`Error fetching course_term ${id}:`, error)
      });
    })
    console.log(this.courseTerms);
  }

}
