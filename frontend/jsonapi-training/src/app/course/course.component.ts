import { Component, Input } from '@angular/core';
import { CommonModule} from '@angular/common';
import { Course } from '../course';
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-course',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterOutlet],
  templateUrl: './course.component.html',
  styleUrl: './course.component.css'
})
export class CourseComponent {
  @Input() course!: Course;
}
