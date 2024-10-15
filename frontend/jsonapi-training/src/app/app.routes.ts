import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CatalogComponent } from './catalog/catalog.component';
import { DetailsComponent } from './details/details.component';

const routes: Routes = [
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

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    useHash: true,
    scrollPositionRestoration: 'enabled', // appears not to work...
  })],

  exports: [RouterModule]
})
export class AppRoutingModule { }

