import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Course } from '../models/course.model';
import { Jsona } from 'jsona';

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private apiUrl = 'http://localhost:8000/v1/courses/';
  private jsona = new Jsona();

  constructor(private http: HttpClient) {}

  getCourses(): Observable<Course[]> {
    return this.http.get(this.apiUrl, this.getHttpOptions()).pipe(
      map((response: any) => this.jsona.deserialize(response) as Course[])
    );
  }

  createCourse(course: Course): Observable<Course> {
    const courseWithJsonApiType = { ...course, type: 'courses' };
    const serializedData = this.jsona.serialize({
      stuff: courseWithJsonApiType,
      includeNames: []
    });
    return this.http.post(this.apiUrl, serializedData, this.getHttpOptions()).pipe(
      map((response: any) => this.jsona.deserialize(response) as Course)
    );
  }

  // for the time being, get a new token via postman and then copy it here:
  private getHttpOptions() {
    return {
      headers: new HttpHeaders({ 'Content-Type': 'application/vnd.api+json', 'Authorization': 'Bearer ubjJVVdwGo8NulBqctCAKgVdIfFyzW' })
    };
  }
}
