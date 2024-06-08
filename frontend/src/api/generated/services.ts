import type { CancelablePromise } from './core/CancelablePromise';
import type { BaseHttpRequest } from './core/BaseHttpRequest';

import type { Vote,VotesQueryResponse,PlenarySessionsQueryResponse,Statistics } from './models';

export type VotesData = {
        Index: {
                    /**
 * Results page
 */
page?: number
/**
 * Number of results per page
 */
pageSize?: number
                    
                };
Search: {
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
                    
                };
GetVote: {
                    voteId: string
                    
                };
GetVoteCsv: {
                    voteId: string
                    
                };
    }

export type PlenarySessionsData = {
        GetSessions: {
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
                    
                };
    }

export type MiscellaneousData = {
        
    }

export class VotesService {

	constructor(public readonly httpRequest: BaseHttpRequest) {}

	/**
	 * List votes
	 * List votes in chronological order.
	 * @returns VotesQueryResponse Ok
	 * @throws ApiError
	 */
	public index(data: VotesData['Index'] = {}): CancelablePromise<VotesQueryResponse> {
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
	public search(data: VotesData['Search'] = {}): CancelablePromise<VotesQueryResponse> {
		const {
q,
page = 1,
pageSize = 20,
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
	public getVote(data: VotesData['GetVote']): CancelablePromise<Vote> {
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
	public getVoteCsv(data: VotesData['GetVoteCsv']): CancelablePromise<void> {
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

export class PlenarySessionsService {

	constructor(public readonly httpRequest: BaseHttpRequest) {}

	/**
	 * List sessions
	 * @returns PlenarySessionsQueryResponse Ok
	 * @throws ApiError
	 */
	public getSessions(data: PlenarySessionsData['GetSessions'] = {}): CancelablePromise<PlenarySessionsQueryResponse> {
		const {
status,
page = 1,
pageSize = 20,
sortOrder = 'asc',
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