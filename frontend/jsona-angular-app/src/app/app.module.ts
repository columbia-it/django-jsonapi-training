import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { CourseListComponent } from './components/course-list/course-list.component';
import { CourseDetailComponent } from './components/course-detail/course-detail.component';  // Import CourseDetailComponent

// Define routes, including the new detail route
const routes: Routes = [
  { path: '', redirectTo: '/courses', pathMatch: 'full' },
  { path: 'courses', component: CourseListComponent },
  { path: 'courses/:id', component: CourseDetailComponent }  // Route for course detail
];

@NgModule({
  declarations: [
    AppComponent,
    CourseListComponent,
    CourseDetailComponent  // Declare CourseDetailComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    RouterModule.forRoot(routes)  // Configure routing with RouterModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
