import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { CallbackComponent } from './components/callback/callback.component';
import { ForbiddenComponent } from './components/forbidden/forbidden.component';
import { HomeComponent } from './components/home/home.component';
import { ProtectedComponent } from './components/protected/protected.component';
import { UnauthorizedComponent } from './components/unauthorized/unauthorized.component';
import { CourseListComponent } from './components/course-list/course-list.component';
import { CourseDetailComponent } from './components/course-detail/course-detail.component';
import { InstructorListComponent } from './components/instructor-list/instructor-list.component';
import { PeopleListComponent } from './components/people-list/people-list.component';

const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'home' },
  {
    path: 'home',
    component: HomeComponent,
    //canActivate: [AutoLoginPartialRoutesGuard],
  },
  {
    path: 'protected',
    component: ProtectedComponent,
    canActivate: [AutoLoginPartialRoutesGuard],
  },
  {
    path: 'forbidden',
    component: ForbiddenComponent,
    canActivate: [AutoLoginPartialRoutesGuard],
  },
  { path: 'courses', component: CourseListComponent, canActivate: [AutoLoginPartialRoutesGuard] },
  { path: 'courses/:id', component: CourseDetailComponent, canActivate: [AutoLoginPartialRoutesGuard] },
  { path: 'instructors', component: InstructorListComponent, canActivate: [AutoLoginPartialRoutesGuard] },
  { path: 'people', component: PeopleListComponent, canActivate: [AutoLoginPartialRoutesGuard] },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: 'callback', component: CallbackComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(appRoutes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

