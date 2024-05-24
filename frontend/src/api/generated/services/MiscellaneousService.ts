import type { Statistics } from '../models';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';



export class MiscellaneousService {

	constructor(public readonly httpRequest: BaseHttpRequest) {}

	/**
	 * List general stats
	 * @returns unknown Ok
	 * @throws ApiError
	 */
	public getStats(): CancelablePromise<Statistics> {
				return this.httpRequest.request({
			method: 'GET',
			url: '/api/stats',
		});
	}

}