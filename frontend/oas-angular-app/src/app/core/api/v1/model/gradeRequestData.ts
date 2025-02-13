/**
 * myapp
 *
 * Contact: alan@columbia.edu
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { GradeRequestDataAttributes } from './gradeRequestDataAttributes';
import { GradeRelationships } from './gradeRelationships';


export interface GradeRequestData { 
    /**
     * The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.
     */
    type: GradeRequestData.TypeEnum;
    attributes?: GradeRequestDataAttributes;
    relationships?: GradeRelationships;
}
export namespace GradeRequestData {
    export type TypeEnum = 'grades';
    export const TypeEnum = {
        Grades: 'grades' as TypeEnum
    };
}


