import { NgModule, inject } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule} from '@angular/common';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { ApiModule, Configuration, ConfigurationParameters } from './core/api/v1';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTabsModule } from '@angular/material/tabs';

import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { CachingInterceptor } from './services/caching.interceptor';

import { CourseListComponent } from './components/course-list/course-list.component';
import { CourseDetailComponent } from './components/course-detail/course-detail.component';
import { AuthConfigModule } from './auth/auth-config.module';
import { CallbackComponent } from './callback/callback.component';
import { ForbiddenComponent } from './forbidden/forbidden.component';
import { HomeComponent } from './home/home.component';
import { NavigationComponent } from './navigation/navigation.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import { ProtectedComponent } from './protected/protected.component';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { InstructorListComponent } from './components/instructor-list/instructor-list.component';

export function apiConfigFactory(): Configuration {
  const oidcSecurityService = inject(OidcSecurityService);
  var conf: any = null; // I'm sure this is not the right way to do this.
  oidcSecurityService.getAccessToken().subscribe((token) => {
    conf = new Configuration({
      basePath: "http://localhost:8000",
      credentials: {'oauth2': token}
    });
    console.log('token:' + token);
    console.log('conf:');
    console.log(conf);
  });
  console.log('conf outer:');
  console.log(conf);
  return conf;
}
@NgModule({
  declarations: [
    AppComponent,
    CourseListComponent,
    CourseDetailComponent,
    CallbackComponent,
    ForbiddenComponent,
    HomeComponent,
    NavigationComponent,
    UnauthorizedComponent,
    ProtectedComponent,
    InstructorListComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    AppRoutingModule,
    ApiModule.forRoot(apiConfigFactory),
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,  // Required for Material animations
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatIconModule,
    MatPaginatorModule,
    MatTabsModule,
    AuthConfigModule,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: CachingInterceptor, multi: true },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
