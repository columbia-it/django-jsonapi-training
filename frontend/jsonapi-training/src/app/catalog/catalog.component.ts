import { Component } from '@angular/core';
import { CourseComponent} from '../course/course.component';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CourseComponent],
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.css'],
})
export class CatalogComponent {
  title = 'catalog';

}
