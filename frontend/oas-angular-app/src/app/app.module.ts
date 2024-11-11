import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { ApiModule, Configuration, ConfigurationParameters } from './core/api/v1';
import { HttpClientModule } from '@angular/common/http';
import { CourseListComponent } from './components/course-list/course-list.component';
import { CourseDetailComponent } from './components/course-detail/course-detail.component';

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    basePath: "http://localhost:8000",
    credentials: { 'oauth2': 'iFxh15ZDzM6as7FmFWKmuJbI5YasKH' }
  }
  return new Configuration(params);
}
@NgModule({
  declarations: [
    AppComponent,
    CourseListComponent,
    CourseDetailComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ApiModule.forRoot(apiConfigFactory),
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
