import { Routes } from '@angular/router';
import { CatalogComponent } from './catalog/catalog.component';
import {DetailsComponent } from './details/details.component';

export const routes: Routes = [
  {
    path: '',
    component: CatalogComponent,
    title: 'home page'
  },
  {
    path: 'details/:id',
    component: DetailsComponent,
    title: 'Course details'
  },
];
