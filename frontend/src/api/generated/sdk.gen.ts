// This file is auto-generated by @hey-api/openapi-ts

import { createClient, createConfig, type OptionsLegacyParser } from '@hey-api/client-fetch';
import type { GetVotesData, GetVotesError, GetVotesResponse, SearchVotesData, SearchVotesError, SearchVotesResponse, GetVoteData, GetVoteError, GetVoteResponse, GetVoteCsvData, GetSessionsData, GetSessionsError, GetSessionsResponse, GetStatsError, GetStatsResponse } from './types.gen';

export const client = createClient(createConfig({
    throwOnError: true
}));

/**
 * List votes
 * List votes in chronological order.
 */
export const getVotes = <ThrowOnError extends boolean = true>(options?: OptionsLegacyParser<GetVotesData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetVotesResponse, GetVotesError, ThrowOnError>({
        ...options,
        url: '/api/votes'
    });
};

/**
 * Search votes
 * Search votes by title and reference. This endpoint returns a maximum of 1,000
 * results, even if more than 1,000 votes match the search query.
 *
 */
export const searchVotes = <ThrowOnError extends boolean = true>(options?: OptionsLegacyParser<SearchVotesData, ThrowOnError>) => {
    return (options?.client ?? client).get<SearchVotesResponse, SearchVotesError, ThrowOnError>({
        ...options,
        url: '/api/votes/search'
    });
};

/**
 * Get vote
 * Get information about a vote. This includes metadata (e.g. vote title and
 * timestamp), aggregated statistics, and the votes of individual MEPs.
 *
 */
export const getVote = <ThrowOnError extends boolean = true>(options: OptionsLegacyParser<GetVoteData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetVoteResponse, GetVoteError, ThrowOnError>({
        ...options,
        url: '/api/votes/{vote_id}'
    });
};

/**
 * Get vote as CSV
 * Get votes of individual MEPs as CSV.
 *
 */
export const getVoteCsv = <ThrowOnError extends boolean = true>(options: OptionsLegacyParser<GetVoteCsvData, ThrowOnError>) => {
    return (options?.client ?? client).get<void, unknown, ThrowOnError>({
        ...options,
        url: '/api/votes/{vote_id}.csv'
    });
};

/**
 * List sessions
 */
export const getSessions = <ThrowOnError extends boolean = true>(options?: OptionsLegacyParser<GetSessionsData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetSessionsResponse, GetSessionsError, ThrowOnError>({
        ...options,
        url: '/api/sessions'
    });
};

/**
 * List general stats
 */
export const getStats = <ThrowOnError extends boolean = true>(options?: OptionsLegacyParser<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetStatsResponse, GetStatsError, ThrowOnError>({
        ...options,
        url: '/api/stats'
    });
};