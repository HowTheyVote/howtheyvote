import type { PlenarySessionsQueryResponse } from '../models';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export type TDataGetSessions = {
                /**
 * Results page
 */
page?: number
/**
 * Number of results per page
 */
pageSize?: number
/**
 * Sort order
 */
sortOrder?: 'asc' | 'desc'
status?: 'current' | 'past' | 'upcoming'
                
            }

export class PlenarySessionsService {

	constructor(public readonly httpRequest: BaseHttpRequest) {}

	/**
	 * List sessions
	 * @returns PlenarySessionsQueryResponse Ok
	 * @throws ApiError
	 */
	public getSessions(data: TDataGetSessions = {}): CancelablePromise<PlenarySessionsQueryResponse> {
		const {
page = 1,
pageSize = 20,
sortOrder,
status,
} = data;
		return this.httpRequest.request({
			method: 'GET',
			url: '/api/sessions',
			query: {
				status, page, page_size: pageSize, sort_order: sortOrder
			},
		});
	}

}