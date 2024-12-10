import { Injectable } from '@angular/core';
import { HttpResponse, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class HttpCacheService {
  private cacheKey = 'httpCache';
  private cacheVersion = '1.0'; // Include cacheVersion
  private requests: Map<string, { response: HttpResponse<any>, timestamp: number }> = new Map();
  private cacheDuration = 300000; // Cache duration in milliseconds (e.g., 5 minutes)
  private maxCacheEntries = 50; // Maximum number of cache entries

  constructor() {
    this.loadCacheFromStorage();
  }

  get(url: string): HttpResponse<any> | undefined {
    const cacheEntry = this.requests.get(url);
    if (!cacheEntry) {
      return undefined;
    }

    const isExpired = (Date.now() - cacheEntry.timestamp) > this.cacheDuration;
    if (isExpired) {
      this.requests.delete(url);
      this.saveCacheToStorage();
      return undefined;
    }

    // Move the accessed entry to the end to mark it as recently used
    this.requests.delete(url);
    this.requests.set(url, cacheEntry);

    return cacheEntry.response;
  }

  put(url: string, response: HttpResponse<any>): void {
    const cacheEntry = {
      response: response,
      timestamp: Date.now()
    };

    // Remove existing entry if it exists to update its position
    if (this.requests.has(url)) {
      this.requests.delete(url);
    }

    this.requests.set(url, cacheEntry);

    // Enforce cache size limit
    if (this.requests.size > this.maxCacheEntries) {
      // Remove the least recently used (first) entry
      const lruKey = this.requests.keys().next().value;
      this.requests.delete(lruKey);
      console.warn(`Cache size limit reached. Removed LRU cache entry for URL: ${lruKey}`);
    }

    this.saveCacheToStorage();
  }

  invalidateUrl(url: string): void {
    this.requests.delete(url);
    this.saveCacheToStorage();
  }

  invalidateCache(): void {
    this.requests.clear();
    sessionStorage.removeItem(this.cacheKey);
  }

  private saveCacheToStorage(): void {
    try {
      const cacheObj: any = {
        version: this.cacheVersion, // Include version in the saved object
        entries: {},
      };
      this.requests.forEach((cacheEntry, url) => {
        const response = cacheEntry.response;
        cacheObj.entries[url] = {
          response: {
            body: response.body,
            status: response.status,
            statusText: response.statusText,
            headers: response.headers.keys().reduce((acc: any, key: string) => {
              acc[key] = response.headers.getAll(key);
              return acc;
            }, {}),
            url: response.url || '',
          },
          timestamp: cacheEntry.timestamp,
        };
      });
      const cacheString = JSON.stringify(cacheObj);
      sessionStorage.setItem(this.cacheKey, cacheString);
    } catch (e) {
      if (this.isQuotaExceeded(e)) {
        console.error('Cache storage quota exceeded. Handling cache overflow with LRU eviction.');
        this.handleCacheOverflow();
      } else {
        console.error('Error saving cache to storage:', e);
      }
    }
  }

  private loadCacheFromStorage(): void {
    try {
      const cacheString = sessionStorage.getItem(this.cacheKey);
      if (cacheString) {
        const cacheObj = JSON.parse(cacheString);

        // Check if the cache version matches
        if (cacheObj.version !== this.cacheVersion) {
          console.warn('Cache version mismatch. Invalidating cache.');
          this.invalidateCache();
          return;
        }

        const entries = cacheObj.entries || {};
        Object.keys(entries).forEach((url) => {
          const cachedEntry = entries[url];

          if (cachedEntry && cachedEntry.response) {
            const cachedResponse = cachedEntry.response;
            const headers = new HttpHeaders(cachedResponse.headers || {});

            const response = new HttpResponse({
              body: cachedResponse.body,
              status: cachedResponse.status,
              statusText: cachedResponse.statusText,
              headers: headers,
              url: cachedResponse.url,
            });

            if (cachedEntry.timestamp) {
              this.requests.set(url, {
                response: response,
                timestamp: cachedEntry.timestamp,
              });
            } else {
              console.warn(`Cache entry for URL: ${url} is missing a timestamp. Entry will be skipped.`);
            }
          } else {
            console.warn(`Invalid or incomplete cache entry for URL: ${url}. Entry will be skipped.`);
          }
        });
      }
    } catch (e) {
      console.error('Error loading cache from storage:', e);
      this.invalidateCache();
    }
  }

  private isQuotaExceeded(e: any): boolean {
    let quotaExceeded = false;
    if (e) {
      if (e.code) {
        switch (e.code) {
          case 22:
            quotaExceeded = true;
            break;
          case 1014:
            // Firefox
            if (e.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
              quotaExceeded = true;
            }
            break;
        }
      } else if (e.number === -2147024882) {
        // Internet Explorer 8
        quotaExceeded = true;
      }
    }
    return quotaExceeded;
  }

  private handleCacheOverflow(): void {
    if (this.requests.size > 0) {
      // Remove the least recently used (LRU) item
      const lruKey = this.requests.keys().next().value;
      this.requests.delete(lruKey);
      console.warn(`Removed LRU cache entry for URL: ${lruKey} due to storage quota.`);

      try {
        this.saveCacheToStorage();
      } catch (e) {
        if (this.isQuotaExceeded(e)) {
          // Recursively handle overflow
          this.handleCacheOverflow();
        } else {
          console.error('Error saving cache to storage after eviction:', e);
        }
      }
    } else {
      console.error('Cache is empty, but storage quota exceeded.');
      // Optionally clear sessionStorage or notify the user
      sessionStorage.clear();
    }
  }
}
