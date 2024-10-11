import { Injectable } from '@angular/core';
import { Course } from './course';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {

  constructor() {
  }
  protected url = 'http://localhost:3000/courses';

  async getAllCourses(): Promise<Course[]> {
    const data = await fetch(this.url);
    return (await data.json()) ?? [];
  }

  async getCourseById(id: string): Promise<Course | undefined> {
    const data = await fetch(`${this.url}/${id}`);
    return (await data.json()) ?? {};
  }

  submitCourse(name: string, description: string) {
    console.log(
      `Courses application received: name: ${name}, description: ${description}`
    );
  }
}
