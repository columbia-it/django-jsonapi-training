import { Component, OnInit, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmLogoutDialogComponent } from './components/confirm-logout-dialog/confirm-logout-dialog.component';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  isAuthenticated: boolean = false;
  userData: any;
  private snackBar: any;

  constructor(
    private dialog: MatDialog,
    private router: Router,
    private oidcSecurityService: OidcSecurityService
  ) {}

  ngOnInit(): void {
    this.oidcSecurityService.checkAuth().subscribe(
      ({ isAuthenticated, userData }) => {
        this.isAuthenticated = isAuthenticated;
        this.userData = userData;
      }
    );
  }

  login(): void {
    this.oidcSecurityService.authorize();
  }
  logout(): void {
    const dialogRef = this.dialog.open(ConfirmLogoutDialogComponent);

    dialogRef.afterClosed().subscribe((result) => {
      if (result === 'confirm') {
        // User confirmed logout
        this.oidcSecurityService.logoff().subscribe({
          next: () => {
            // Logoff successful
            this.router.navigate(['/home']);
          },
          error: (error) => {
            // Handle errors or cancellations
            console.error('Error during logout:', error);

            this.snackBar.open('Logout failed. Please try again.', 'Close', { duration: 5000 });

            // Navigate to a safe route
            sessionStorage.setItem('activeTabIndex', String(0)); // reset to the home tab
            this.router.navigate(['/home']);
          },
        });
      } else {
        // User canceled logout
        console.log('Logout canceled');
      }
    });
  }

  profile(): void {
    // Navigate to the home page to display user info for now
    sessionStorage.setItem('activeTabIndex', String(0)); // reset to the home tab NOT WORKING
    this.router.navigate(['/home']);
  }

}
