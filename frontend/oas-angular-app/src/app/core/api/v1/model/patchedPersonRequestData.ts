/**
 * myapp
 *
 * Contact: alan@columbia.edu
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { PatchedPersonRequestDataAttributes } from './patchedPersonRequestDataAttributes';
import { PatchedPersonRequestDataRelationships } from './patchedPersonRequestDataRelationships';


export interface PatchedPersonRequestData { 
    /**
     * The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.
     */
    type: PatchedPersonRequestData.TypeEnum;
    id: any | null;
    attributes?: PatchedPersonRequestDataAttributes;
    relationships?: PatchedPersonRequestDataRelationships;
}
export namespace PatchedPersonRequestData {
    export type TypeEnum = 'people';
    export const TypeEnum = {
        People: 'people' as TypeEnum
    };
}

