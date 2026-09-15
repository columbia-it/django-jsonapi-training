import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { JsonApiResource, Pagination } from '../../core/api/json-api';
import { ResourceName } from '../../core/api/models';
import { ResourceStore } from '../../core/api/resources';

@Component({
  selector: 'app-resource-list',
  imports: [FormsModule, RouterLink],
  styleUrl: './resource-list.css',
  templateUrl: './resource-list.html',
})
export class ResourceList implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly store = inject(ResourceStore);
  readonly resource = this.route.snapshot.data['resource'] as ResourceName;
  readonly items = signal<JsonApiResource[]>([]);
  readonly included = signal<JsonApiResource[]>([]);
  readonly pagination = signal<Pagination | undefined>(undefined);
  readonly loading = signal(false);
  readonly error = signal('');
  search = '';
  page = 1;
  pageSize = 10;
  ngOnInit(): void {
    const saved = sessionStorage.getItem(`list:${this.resource}`);
    if (saved) {
      ({ search: this.search, page: this.page, pageSize: this.pageSize } = JSON.parse(saved));
      this.pageSize ||= 10;
    }
    this.load();
  }
  load(page = this.page): void {
    this.page = page;
    this.loading.set(true);
    this.error.set('');
    sessionStorage.setItem(
      `list:${this.resource}`,
      JSON.stringify({ search: this.search, page, pageSize: this.pageSize }),
    );
    this.store
      .list(this.resource, {
        search: this.search,
        page,
        pageSize: this.pageSize,
        ordering:
          this.resource === 'courses'
            ? 'course_identifier'
            : this.resource === 'course_terms'
              ? 'term_identifier'
              : this.resource === 'people'
                ? 'name'
                : undefined,
        include:
          this.resource === 'courses'
            ? 'course_terms'
            : this.resource === 'course_terms'
              ? 'course,instructors,instructors.person'
              : this.resource === 'instructors'
                ? 'person,course_terms,course_terms.course'
                : this.resource === 'people'
                  ? 'instructor'
                  : undefined,
      })
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (response) => {
          this.items.set(response.data);
          this.included.set(response.included ?? []);
          this.pagination.set(response.meta?.pagination);
        },
        error: (error) =>
          this.error.set(error?.error?.errors?.[0]?.detail ?? 'The API request failed.'),
      });
  }
  submit(): void {
    this.load(1);
  }
  clearSearch(): void {
    this.search = '';
    this.load(1);
  }
  changePageSize(): void {
    this.load(1);
  }
  title(): string {
    return this.resource === 'course_terms'
      ? 'Course terms'
      : this.resource[0].toUpperCase() + this.resource.slice(1);
  }
  primary(item: JsonApiResource): string {
    return String(
      item.attributes['course_identifier'] ??
        item.attributes['name'] ??
        item.attributes['term_identifier'] ??
        this.relatedName(item) ??
        item.id,
    );
  }
  secondary(item: JsonApiResource): string {
    return String(
      item.attributes['course_name'] ?? (this.resource === 'instructors' ? 'Instructor' : ''),
    );
  }
  description(item: JsonApiResource): string {
    const description = String(item.attributes['course_description'] ?? '');
    return description === item.attributes['course_name'] ? '' : description;
  }
  termsFor(item: JsonApiResource): JsonApiResource[] {
    return this.related(item, 'course_terms');
  }
  termLabel(term: JsonApiResource): string {
    return String(term.attributes['term_identifier'] ?? term.id).slice(0, 5);
  }
  related(item: JsonApiResource, relationship: string): JsonApiResource[] {
    const linkage = item.relationships?.[relationship]?.data;
    const identifiers = Array.isArray(linkage) ? linkage : linkage ? [linkage] : [];
    const ids = new Set(identifiers.map((related) => `${related.type}:${related.id}`));
    return this.included().filter((related) => ids.has(`${related.type}:${related.id}`));
  }
  relationshipId(item: JsonApiResource, relationship: string): string | null {
    const linkage = item.relationships?.[relationship]?.data;
    return linkage && !Array.isArray(linkage) ? linkage.id : null;
  }
  courseCode(term: JsonApiResource): string {
    const course = this.related(term, 'course')[0];
    return String(
      course?.attributes['course_identifier'] ??
        term.attributes['term_identifier']?.toString().slice(5) ??
        '',
    );
  }
  courseName(term: JsonApiResource): string {
    return String(this.related(term, 'course')[0]?.attributes['course_name'] ?? '');
  }
  personName(instructor: JsonApiResource): string {
    return String(this.related(instructor, 'person')[0]?.attributes['name'] ?? instructor.id);
  }
  private relatedName(item: JsonApiResource): unknown {
    const person = item.relationships?.['person']?.data;
    if (!person || Array.isArray(person)) return undefined;
    return this.included().find(
      (resource) => resource.type === person.type && resource.id === person.id,
    )?.attributes['name'];
  }
}
