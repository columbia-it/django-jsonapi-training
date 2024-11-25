import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CoursesService, InstructorsService } from '../../core/api/v1';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrl: './course-detail.component.css'
})
export class CourseDetailComponent implements OnInit {
  course: any;
  instructors: { [key: string]: any } = {};

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService,
    private instructorsService: InstructorsService
  ) {}

  ngOnInit() {
    const courseId = this.route.snapshot.paramMap.get('id');

    if (courseId) {
      this.coursesService.coursesRetrieve({
        id: courseId,
        include: ['course_terms']
      }).subscribe(
	(course) => {
	  this.course = course;
	  console.log(this.course)
    this.loadInstructors();
	},
	(error) => console.error('Error:', error)
      );
    }
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
      }).subscribe(
        (instructor) => (this.instructors[instructorId] = instructor),
        (error) => console.error(`Error fetching instructor ${id}:`, error)
      );
    })
    console.log(this.instructors);
  }
}
