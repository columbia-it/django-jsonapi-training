import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  template: `<section class="hero">
    <p class="eyebrow">Example browser client</p>
    <h1>Explore the training API</h1>
    <p>
      This Angular client consumes the Django REST Framework JSON:API endpoints directly, with typed
      resources, relationship includes, pagination, and OIDC authorization.
    </p>
    <a class="button" routerLink="/courses">Browse courses</a>
  </section>`,
  styles: [
    `
      .hero {
        max-width: 48rem;
        padding: 4rem 0;
      }
      .eyebrow {
        color: #486581;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .hero p {
        font-size: 1.15rem;
        line-height: 1.7;
      }
      .button {
        display: inline-block;
        margin-top: 1rem;
      }
    `,
  ],
})
export class Home {}
