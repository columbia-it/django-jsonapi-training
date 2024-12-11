import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CoursesService, InstructorsService } from '../../core/api/v1';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrl: './course-detail.component.css'
})
export class CourseDetailComponent implements OnInit {
  course: any;
  instructors: { [key: string]: any } = {};
  origin: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService,
    private instructorsService: InstructorsService,
    private router: Router
  ) {}

  ngOnInit() {
    const courseId = this.route.snapshot.paramMap.get('id');
    this.origin = this.route.snapshot.queryParamMap.get('origin');

    if (courseId) {
      this.coursesService.coursesRetrieve({
        id: courseId,
        include: ['course_terms']
      }).subscribe({
        next: (course) => {
          this.course = course;
          this.loadInstructors();
        },
        error: (error) => console.error('Error:', error)
      });
    }
  }

  goBack() {
    this.router.navigate([this.origin ? this.origin : '/home']);
  }
  loadInstructors() {
    if (!this.course?.included) return;
    const instructorIds = new Set(
      this.course.included
        .filter((item: any) => item.type === 'course_terms')  // Filter for course_terms
        .flatMap((term: any) => term.relationships.instructors.data.map((inst: any) => inst.id))
    );

    instructorIds.forEach((id) => {
      const instructorId = id as string;

      this.instructorsService.instructorsRetrieve({
        id: instructorId,
        include: ['person']
      }).subscribe({
        next: (instructor) => (this.instructors[instructorId] = instructor),
        error: (error) => console.error(`Error fetching instructor ${id}:`, error)
      });
    })
  }
}
