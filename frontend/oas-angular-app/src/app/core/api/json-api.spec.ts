import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL, JsonApiClient } from './json-api';

describe('JsonApiClient', () => {
  let client: JsonApiClient;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_BASE_URL, useValue: 'http://example.test/v1' },
      ],
    });
    client = TestBed.inject(JsonApiClient);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('uses JSON:API collection query parameters', () => {
    client
      .collection('courses', {
        search: 'biology',
        page: 2,
        pageSize: 20,
        ordering: 'course_identifier',
        include: 'course_terms',
      })
      .subscribe();
    const request = http.expectOne((request) => request.url === 'http://example.test/v1/courses/');
    expect(request.request.params.get('filter[search]')).toBe('biology');
    expect(request.request.params.get('page[number]')).toBe('2');
    expect(request.request.params.get('page[size]')).toBe('20');
    expect(request.request.params.get('sort')).toBe('course_identifier');
    expect(request.request.params.get('include')).toBe('course_terms');
    request.flush({ data: [] });
  });

  it('requests compound documents for detail views', () => {
    client.item('courses', 'abc/123', 'course_terms').subscribe();
    const request = http.expectOne(
      (request) => request.url === 'http://example.test/v1/courses/abc%2F123/',
    );
    expect(request.request.params.get('include')).toBe('course_terms');
    request.flush({ data: { type: 'courses', id: 'abc/123', attributes: {} } });
  });
});
