import { NgModule, inject } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule} from '@angular/common';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { ApiModule, Configuration, ConfigurationParameters } from './core/api/v1';
import { HttpClientModule } from '@angular/common/http';
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

// export function apiConfigFactory(): Configuration {
//   const params: ConfigurationParameters = {
//     basePath: "http://localhost:8000",
//   }
//   return new Configuration(params);
// }
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
    ProtectedComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    AppRoutingModule,
    ApiModule,
    HttpClientModule,
    AuthConfigModule,
  ],
  providers: [
  {
    provide: Configuration,
    useFactory: (authService: OidcSecurityService) => new Configuration(
      {
        basePath: "http://localhost:8000",
        //credentials: { 'oauth2': authService.getAccessToken.bind(authService) }
        credentials: { 'oauth2': 'bb0CKaLe03tapg2yjKm2g0URirtfuV' }
      }
    ),
    deps: [OidcSecurityService],
    multi: false
      }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
