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


export interface PatchedGradeRequestData { 
    /**
     * The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.
     */
    type: PatchedGradeRequestData.TypeEnum;
    id: any | null;
    attributes?: GradeRequestDataAttributes;
    relationships?: GradeRelationships;
}
export namespace PatchedGradeRequestData {
    export type TypeEnum = 'grades';
    export const TypeEnum = {
        Grades: 'grades' as TypeEnum
    };
}


