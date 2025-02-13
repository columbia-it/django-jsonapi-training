/**
 * myapp
 *
 * Contact: alan@columbia.edu
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


export interface ResourceIdentifier1Data { 
    id: string;
    /**
     * The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.
     */
    type: ResourceIdentifier1Data.TypeEnum;
}
export namespace ResourceIdentifier1Data {
    export type TypeEnum = 'course_terms';
    export const TypeEnum = {
        CourseTerms: 'course_terms' as TypeEnum
    };
}


