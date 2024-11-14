import { NgModule } from '@angular/core';
import { AuthModule } from 'angular-auth-oidc-client';


@NgModule({
  imports: [AuthModule.forRoot({
    config: {
      authority: 'http://localhost:8000/o/.well-known/openid-configuration/',
      redirectUrl: window.location.origin,
      postLogoutRedirectUri: window.location.origin,
      clientId: 'demo_djt_web_client',
      scope: 'openid profile email read auth-columbia demo-djt-sla-bronze https://api.columbia.edu/scope/group',
      responseType: 'code',
      silentRenew: true,
      useRefreshToken: true,
      renewTimeBeforeTokenExpiresInSeconds: 30,
    }
  })],
  exports: [AuthModule],
})
export class AuthConfigModule {}
