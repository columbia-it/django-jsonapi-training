# Angular frontend single-page client applications

## Automated models and services via @openapitools/openapi-generator-cli

See [this tutorial](https://www.kevinboosten.dev/how-i-use-an-openapi-spec-in-my-angular-projects).

### Steps to build it

1. Start with a new app module. In ng 18+ you have to explicitly say you want an app.module:

```
ng new --standalone false oas-angular-app
```

2. Install the openapi-generator-cli:

```
npm i @openapitools/openapi-generator-cli -D
```

Note that [openapi-generator](https://github.com/OpenAPITools/openapi-generator) is a Jave app
so you may have to install and/or upgrade your JRE.

Here's how I did it for MacOS:

```
brew tap AdoptOpenJDK/openjdk
brew install --cask adoptopenjdk11
which java
export JAVA_HOME=`/usr/libexec/java_home -v 1.11`
java -version
openjdk version "11.0.11" 2021-04-20
OpenJDK Runtime Environment AdoptOpenJDK-11.0.11+9 (build 11.0.11+9)
```

3. Add a build script to run openapi-generator.  Add this to `package.json`:

```diff
diff --git a/frontend/oas-angular-app/package.json b/frontend/oas-angular-app/package.json
index 7b76dd3..9aaa370 100644
--- a/frontend/oas-angular-app/package.json
+++ b/frontend/oas-angular-app/package.json
@@ -6,7 +6,9 @@
     "start": "ng serve",
     "build": "ng build",
     "watch": "ng build --watch --configuration development",
-    "test": "ng test"
+    "test": "ng test",
+    "generate:api": "openapi-generator-cli generate -p=removeOperationIdPrefix=true -i ../../docs/schemas/openapi.yaml -g typescript-angular -o src/app/core/api/v1"
   },
```


4. Generate the API client code:

```
npm run generate:api
```

5. Make some components

```
mkdir src/app/components
cd src/app/components
ng generate component CourseList
ng generate component CourseDetail
```

Here's a very basic example:

```typescript
// app/components/course-list/course-list.component.ts
import { Component, OnInit } from '@angular/core';
import { CoursesService, Course } from '../../core/api/v1';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.css'
})
export class CourseListComponent implements OnInit {
  courses: any;

  constructor(private coursesService: CoursesService) {}

  ngOnInit() {
    this.coursesService.coursesList().subscribe(
      (courses) => {
        this.courses = courses;
        console.log(this.courses)
      },
      (error) => console.error('Error:', error)
    );
  }
}
```

Unlike `jsona` this package doesn't know the details of a JSONAPI.org spec so you need to drill down into the
response a bit in this example:

```html
<!-- app/components/course-list/course-list.component.html -->
<h2>Course List</h2>
Page {{ courses.meta.pagination.page }} (length {{courses.data.length }}) of {{ courses.meta.pagination.pages }}
<ul>
  <li *ngFor="let course of courses.data">
    <a [routerLink]="['/courses', course.id]">{{ course.attributes.course_identifier }}</a>:
      {{ course.attributes.course_name }}
  </li>
</ul>

```