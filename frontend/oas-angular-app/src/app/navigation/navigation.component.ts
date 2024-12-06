import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';

interface Tab {
  label: string;
  route?: string; // Route to navigate to
  action?: () => void; // Action to perform for the tab
}

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.css']
})
export class NavigationComponent implements OnInit {
  isAuthenticated: boolean = false;

  // Tabs configuration
  tabs: Tab[] = [];
  activeTabIndex: number = 0; // Default active tab index

  constructor(private oidcSecurityService: OidcSecurityService, private router: Router) {}

  ngOnInit(): void {
    // Subscribe to the authentication state
    this.oidcSecurityService.isAuthenticated$.subscribe(({ isAuthenticated }) => {
      this.isAuthenticated = isAuthenticated;

      // Update tabs dynamically based on authentication state
      this.updateTabs();
    });

    // Restore active tab index from sessionStorage
    const savedTabIndex = sessionStorage.getItem('activeTabIndex');
    this.activeTabIndex = savedTabIndex ? parseInt(savedTabIndex, 10) : 0;

    // Initialize tabs
    this.updateTabs();
  }

  updateTabs(): void {
    this.tabs = [
      { label: 'Home', route: '/home' },
      { label: 'Courses', route: '/courses' },
      { label: 'Instructors', route: '/instructors' },
      { label: 'People', route: '/people' },
      ...(this.isAuthenticated
        ? [{ label: 'Logout', action: () => this.logout() }]
        : []) // Only add "Logout" if authenticated
    ];
  }

  logout(): void {
    this.oidcSecurityService.logoff().subscribe(() => {
      this.router.navigate(['/home']);
    });
  }

  login(): void {
    this.oidcSecurityService.authorize();
  }

  onTabChange(index: number): void {
    const tab = this.tabs[index];
    this.activeTabIndex = index; // Save the active tab index
    sessionStorage.setItem('activeTabIndex', String(index)); // Persist the active tab index

    if (tab.route) {
      this.router.navigate([tab.route]);
    } else if (tab.action) {
      tab.action();
    }
  }
}
