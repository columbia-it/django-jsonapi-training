import { KeyValuePipe } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { JsonApiItem, JsonApiResource } from '../../core/api/json-api';
import { ResourceName } from '../../core/api/models';
import { ResourceStore } from '../../core/api/resources';

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
      item.attributes['course_identifier'] ?? item.attributes['name'] ?? `${item.type} ${item.id}`,
    );
  }
  label(value: string): string {
    return value.replaceAll('_', ' ');
  }
  visible(value: unknown): string {
    return value === null || value === '' ? '—' : String(value);
  }
}
