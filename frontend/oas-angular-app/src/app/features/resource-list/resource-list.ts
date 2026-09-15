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
  ngOnInit(): void {
    const saved = sessionStorage.getItem(`list:${this.resource}`);
    if (saved) ({ search: this.search, page: this.page } = JSON.parse(saved));
    this.load();
  }
  load(page = this.page): void {
    this.page = page;
    this.loading.set(true);
    this.error.set('');
    sessionStorage.setItem(`list:${this.resource}`, JSON.stringify({ search: this.search, page }));
    this.store
      .list(this.resource, {
        search: this.search,
        page,
        pageSize: 20,
        ordering:
          this.resource === 'courses'
            ? 'course_identifier'
            : this.resource === 'people'
              ? 'name'
              : undefined,
        include: this.resource === 'instructors' ? 'person' : undefined,
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
  title(): string {
    return this.resource[0].toUpperCase() + this.resource.slice(1);
  }
  primary(item: JsonApiResource): string {
    return String(
      item.attributes['course_identifier'] ??
        item.attributes['name'] ??
        this.relatedName(item) ??
        item.id,
    );
  }
  secondary(item: JsonApiResource): string {
    return String(
      item.attributes['course_name'] ?? (this.resource === 'instructors' ? 'Instructor' : ''),
    );
  }
  private relatedName(item: JsonApiResource): unknown {
    const person = item.relationships?.['person']?.data;
    if (!person || Array.isArray(person)) return undefined;
    return this.included().find(
      (resource) => resource.type === person.type && resource.id === person.id,
    )?.attributes['name'];
  }
}
