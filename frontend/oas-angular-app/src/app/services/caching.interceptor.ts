// caching.interceptor.ts
import { Injectable } from '@angular/core';
import {
  HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HttpResponse
} from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { HttpCacheService } from './http-cache.service';

@Injectable()
export class CachingInterceptor implements HttpInterceptor {

  constructor(private cacheService: HttpCacheService) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Only intercept GET requests
    if (req.method !== 'GET') {
      return next.handle(req);
    }

    // Attempt to retrieve a cached response
    const cachedResponse = this.cacheService.get(req.urlWithParams);

    if (cachedResponse) {
      // Return the cached response
      return of(cachedResponse.clone());
    }

    // Send request to server and cache the response
    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          this.cacheService.put(req.urlWithParams, event.clone());
        }
      })
    );
  }
}
