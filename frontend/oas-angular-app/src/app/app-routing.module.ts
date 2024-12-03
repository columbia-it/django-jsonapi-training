import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { CallbackComponent } from './callback/callback.component';
import { ForbiddenComponent } from './forbidden/forbidden.component';
import { HomeComponent } from './home/home.component';
import { ProtectedComponent } from './protected/protected.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import { CourseListComponent } from './components/course-list/course-list.component';
import { CourseDetailComponent } from './components/course-detail/course-detail.component';
import { InstructorListComponent } from './components/instructor-list/instructor-list.component';

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
  {
    path: 'courses',
    component: CourseListComponent,
    canActivate: [AutoLoginPartialRoutesGuard],
    // loadChildren: () =>
    //   import('./components/course-list/course-list.component').then((m) => m.CourseListComponent),
    // canLoad: [AutoLoginPartialRoutesGuard],
  },
  { path: 'courses/:id', component: CourseDetailComponent },
  { path: 'instructors', component: InstructorListComponent },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: 'callback', component: CallbackComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(appRoutes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

