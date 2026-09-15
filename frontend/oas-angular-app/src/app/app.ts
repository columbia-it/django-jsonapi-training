import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  private readonly oidc = inject(OidcSecurityService);
  readonly authenticated = () => this.oidc.authenticated().isAuthenticated;
  login(): void {
    this.oidc.authorize();
  }
  logout(): void {
    this.oidc.logoff().subscribe();
  }
}
