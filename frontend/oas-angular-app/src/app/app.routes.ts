import { Routes } from '@angular/router';
import { autoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { Home } from './features/home/home';
import { ResourceDetail } from './features/resource-detail/resource-detail';
import { ResourceList } from './features/resource-list/resource-list';

export const routes: Routes = [
  { path: '', component: Home, title: 'Django JSON:API Training' },
  {
    path: 'courses',
    component: ResourceList,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'courses' },
    title: 'Courses',
  },
  {
    path: 'courses/:id',
    component: ResourceDetail,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'courses' },
    title: 'Course',
  },
  {
    path: 'instructors',
    component: ResourceList,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'instructors' },
    title: 'Instructors',
  },
  {
    path: 'instructors/:id',
    component: ResourceDetail,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'instructors' },
    title: 'Instructor',
  },
  {
    path: 'people',
    component: ResourceList,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'people' },
    title: 'People',
  },
  {
    path: 'people/:id',
    component: ResourceDetail,
    canActivate: [autoLoginPartialRoutesGuard],
    data: { resource: 'people' },
    title: 'Person',
  },
  { path: '**', redirectTo: '' },
];
