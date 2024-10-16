import { Injectable } from '@angular/core';
import { JsonApiDatastoreConfig, JsonApiDatastore, DatastoreConfig } from 'angular2-jsonapi';
import { HttpClient } from '@angular/common/http'
import { Course } from './course';

const config: DatastoreConfig = {
  baseUrl: 'http://localhost:8000/v1/',
  models: {
    courses: Course,
  }
}

@Injectable()
@JsonApiDatastoreConfig(config)
export class Datastore extends JsonApiDatastore {

  constructor(http: HttpClient) {
    super(http);
  }
}
