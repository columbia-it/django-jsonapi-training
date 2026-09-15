import { inject, Injectable } from '@angular/core';
import { CollectionQuery, JsonApiClient, JsonApiCollection } from './json-api';
import { ResourceAttributesMap, ResourceName } from './models';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ResourceStore {
  private readonly api = inject(JsonApiClient);
  list<R extends ResourceName>(
    resource: R,
    query: CollectionQuery,
  ): Observable<JsonApiCollection<ResourceAttributesMap[R]>> {
    return this.api.collection<ResourceAttributesMap[R]>(resource, query);
  }
  get(resource: ResourceName, id: string) {
    const include =
      resource === 'courses'
        ? 'course_terms,course_terms.instructors,course_terms.instructors.person'
        : resource === 'course_terms'
          ? 'course,instructors,instructors.person'
          : resource === 'instructors'
            ? 'person,course_terms,course_terms.course'
            : 'instructor,instructor.course_terms,instructor.course_terms.course';
    return this.api.item<Record<string, unknown>>(resource, id, include);
  }
}
