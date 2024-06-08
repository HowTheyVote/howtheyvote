import type { Vote,VotesQueryResponse } from '../models';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export type TDataIndex = {
                /**
 * Results page
 */
page?: number
/**
 * Number of results per page
 */
pageSize?: number
                
            }
export type TDataSearch = {
                /**
 * Results page
 */
page?: number
/**
 * Number of results per page
 */
pageSize?: number
/**
 * Search query
 */
q?: string
                
            }
export type TDataGetVote = {
                voteId: string
                
            }
export type TDataGetVoteCsv = {
                voteId: string
                
            }

export class VotesService {

	constructor(public readonly httpRequest: BaseHttpRequest) {}

	/**
	 * List votes
	 * List votes in chronological order.
	 * @returns VotesQueryResponse Ok
	 * @throws ApiError
	 */
	public index(data: TDataIndex = {}): CancelablePromise<VotesQueryResponse> {
		const {
page = 1,
pageSize = 20,
} = data;
		return this.httpRequest.request({
			method: 'GET',
			url: '/api/votes',
			query: {
				page, page_size: pageSize
			},
		});
	}

	/**
	 * Search votes
	 * Search votes by title and reference. This endpoint returns a maximum of 1,000
 * results, even if more than 1,000 votes match the search query.
 * 
	 * @returns VotesQueryResponse Ok
	 * @throws ApiError
	 */
	public search(data: TDataSearch = {}): CancelablePromise<VotesQueryResponse> {
		const {
page = 1,
pageSize = 20,
q,
} = data;
		return this.httpRequest.request({
			method: 'GET',
			url: '/api/votes/search',
			query: {
				q, page, page_size: pageSize
			},
		});
	}

	/**
	 * Get vote
	 * Get information about a vote. This includes metadata (e.g. vote title and
 * timestamp), aggregated statistics, and the votes of individual MEPs.
 * 
	 * @returns Vote Ok
	 * @throws ApiError
	 */
	public getVote(data: TDataGetVote): CancelablePromise<Vote> {
		const {
voteId,
} = data;
		return this.httpRequest.request({
			method: 'GET',
			url: '/api/votes/{vote_id}',
			path: {
				vote_id: voteId
			},
		});
	}

	/**
	 * Get vote as CSV
	 * Get votes of individual MEPs as CSV.
 * 
	 * @throws ApiError
	 */
	public getVoteCsv(data: TDataGetVoteCsv): CancelablePromise<void> {
		const {
voteId,
} = data;
		return this.httpRequest.request({
			method: 'GET',
			url: '/api/votes/{vote_id}.csv',
			path: {
				vote_id: voteId
			},
		});
	}

}