/**
 * myapp
 *
 * Contact: alan@columbia.edu
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


export interface CourseTermRequestDataAttributes { 
    /**
     * date when this instance becomes valid
     */
    effective_start_date?: string | null;
    /**
     * date when this instance becomes invalid
     */
    effective_end_date?: string | null;
    /**
     * who last modified this instance
     */
    readonly last_mod_user_name?: string | null;
    /**
     * when they modified it
     */
    readonly last_mod_date?: string;
    term_identifier: string;
    audit_permitted_code?: number;
    exam_credit_flag?: boolean;
}

