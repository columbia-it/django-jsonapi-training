import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable, InjectionToken } from '@angular/core';
import { Observable } from 'rxjs';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');
export interface ResourceIdentifier {
  id: string;
  type: string;
}
export interface Relationship {
  data: ResourceIdentifier | ResourceIdentifier[] | null;
}
export interface JsonApiResource<
  T extends object = Record<string, unknown>,
> extends ResourceIdentifier {
  attributes: T;
  relationships?: Record<string, Relationship>;
}
export interface Pagination {
  page: number;
  pages: number;
  count: number;
}
export interface JsonApiCollection<T extends object> {
  data: JsonApiResource<T>[];
  included?: JsonApiResource[];
  meta?: { pagination?: Pagination };
}
export interface JsonApiItem<T extends object> {
  data: JsonApiResource<T>;
  included?: JsonApiResource[];
}
export interface CollectionQuery {
  search?: string;
  page?: number;
  pageSize?: number;
  ordering?: string;
  include?: string;
}

@Injectable({ providedIn: 'root' })
export class JsonApiClient {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);
  collection<T extends object>(
    path: string,
    query: CollectionQuery = {},
  ): Observable<JsonApiCollection<T>> {
    let params = new HttpParams();
    if (query.search) params = params.set('filter[search]', query.search);
    if (query.page) params = params.set('page[number]', query.page);
    if (query.pageSize) params = params.set('page[size]', query.pageSize);
    if (query.ordering) params = params.set('sort', query.ordering);
    if (query.include) params = params.set('include', query.include);
    return this.http.get<JsonApiCollection<T>>(`${this.baseUrl}/${path}/`, { params });
  }
  item<T extends object>(path: string, id: string, include?: string): Observable<JsonApiItem<T>> {
    const params = include ? new HttpParams().set('include', include) : undefined;
    return this.http.get<JsonApiItem<T>>(`${this.baseUrl}/${path}/${encodeURIComponent(id)}/`, {
      params,
    });
  }
}
