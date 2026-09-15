import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import {
  authInterceptor,
  provideAuth,
  withAppInitializerAuthCheck,
} from 'angular-auth-oidc-client';
import { routes } from './app.routes';
import { API_BASE_URL } from './core/api/json-api';

const backend = 'http://localhost:8000';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor()])),
    provideAuth(
      {
        config: {
          authority: `${backend}/o/.well-known/openid-configuration/`,
          redirectUrl: window.location.origin,
          postLogoutRedirectUri: window.location.origin,
          clientId: 'demo_djt_web_client',
          scope:
            'openid profile email read auth-columbia demo-djt-sla-bronze https://api.columbia.edu/scope/group',
          responseType: 'code',
          silentRenew: true,
          useRefreshToken: true,
          disableRefreshTokenOfflineAccessScopeWarning: true,
          renewTimeBeforeTokenExpiresInSeconds: 30,
          secureRoutes: [`${backend}/v1/`],
        },
      },
      withAppInitializerAuthCheck(),
    ),
    { provide: API_BASE_URL, useValue: `${backend}/v1` },
  ],
};
