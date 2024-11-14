import { Component, OnInit, inject } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  private readonly oidcSecurityService = inject(OidcSecurityService);

  ngOnInit() {
    this.oidcSecurityService
      .checkAuth()
      .subscribe(
        ({ isAuthenticated, userData, accessToken, idToken, configId }) => {
          console.log('callback authenticated', isAuthenticated);
        }
      );
  }
}
