import { KeyValuePipe } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { JsonApiItem, JsonApiResource } from '../../core/api/json-api';
import { ResourceName } from '../../core/api/models';
import { ResourceStore } from '../../core/api/resources';

interface RelatedGroup {
  name: string;
  resources: JsonApiResource[];
}

@Component({
  selector: 'app-resource-detail',
  imports: [KeyValuePipe, RouterLink],
  styleUrl: './resource-detail.css',
  templateUrl: './resource-detail.html',
})
export class ResourceDetail implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly store = inject(ResourceStore);
  readonly resource = this.route.snapshot.data['resource'] as ResourceName;
  readonly document = signal<JsonApiItem<Record<string, unknown>> | undefined>(undefined);
  readonly loading = signal(true);
  readonly error = signal('');
  ngOnInit(): void {
    this.store
      .get(this.resource, this.route.snapshot.paramMap.get('id')!)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (result) => this.document.set(result),
        error: (error) =>
          this.error.set(error?.error?.errors?.[0]?.detail ?? 'The API request failed.'),
      });
  }
  heading(item: JsonApiResource): string {
    return String(
      item.attributes['course_identifier'] ??
        item.attributes['name'] ??
        item.attributes['term_identifier'] ??
        `${item.type} ${item.id}`,
    );
  }
  collectionPath(): string {
    return this.resource === 'course_terms' ? 'course-terms' : this.resource;
  }
  routeFor(item: JsonApiResource): string[] | null {
    const route =
      item.type === 'courses'
        ? 'courses'
        : item.type === 'course_terms'
          ? 'course-terms'
          : item.type === 'instructors'
            ? 'instructors'
            : item.type === 'people'
              ? 'people'
              : null;
    return route ? ['/', route, item.id] : null;
  }
  relatedGroups(item: JsonApiResource): RelatedGroup[] {
    const included = this.document()?.included ?? [];
    return Object.entries(item.relationships ?? {})
      .map(([name, relationship]) => {
        const linkage = Array.isArray(relationship.data)
          ? relationship.data
          : relationship.data
            ? [relationship.data]
            : [];
        const ids = new Set(linkage.map((related) => `${related.type}:${related.id}`));
        return {
          name,
          resources: included.filter((related) => ids.has(`${related.type}:${related.id}`)),
        };
      })
      .filter((group) => group.resources.length > 0);
  }
  summary(item: JsonApiResource): string {
    const name = item.attributes['course_name'];
    const description = item.attributes['course_description'];
    if (name && description && name !== description) return `${name} — ${description}`;
    return String(name ?? '');
  }
  label(value: string): string {
    return value.replaceAll('_', ' ');
  }
  visible(value: unknown): string {
    return value === null || value === '' ? '—' : String(value);
  }
}
