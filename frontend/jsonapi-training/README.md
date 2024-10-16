# PORTING NOTES

Trying to use Ivy compiler by rebuilding angular2-jsonapi.
It appears that https://github.com/ghidoz/angular2-jsonapi has abandoned work.
https://github.com/michalkotas/angular2-jsonapi seems to have picked it up and updated it to support
Angular 14+.
I cloned that and have been trying to upgrade package versions. See https://github.com/n2ygk/angular2-jsonapi/tree/npm-updates.

In building this I did:
```
npm run build
```
and then update package.json with this line:
```json
    "angular2-jsonapi": "file:../../../angular2-jsonapi/dist/angular2-jsonapi",
```
and do another `npm i`.

# JsonapiTraining

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 18.2.7.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
