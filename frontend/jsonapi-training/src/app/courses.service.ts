import { Injectable } from '@angular/core';
import { Datastore } from './datastore.service';
import { Course } from './course';
import { JsonApiQueryData} from 'angular2-jsonapi';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {

  constructor(private datastore: Datastore) { }

  getAllCourses() {
    this.datastore.findAll(Course, {
        page: { size: 10, number: 1 },
        filter: {
          title: 'Courses',
        },
    }).subscribe(
        (courses: JsonApiQueryData<Course>) => console.log(courses.getModels())
    );
  }

  getCourseById(id: string) {
    this.datastore.findRecord(Course, id).subscribe(
      (course: Course) => console.log(course)
    );
  }

  submitCourse(name: string, description: string) {
    console.log(
      `Courses application received: name: ${name}, description: ${description}`
    );
  }
}
