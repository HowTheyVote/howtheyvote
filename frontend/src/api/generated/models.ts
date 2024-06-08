/**
 * Member of the European Parliament (MEP)
 */
export type Member = {
	/**
	 * MEP ID. This is the same ID that the European Parliament uses on its website at
 * https://europarl.europa.eu/meps.
	 */
	id: number;
	/**
	 * First name
	 */
	first_name: string;
	/**
	 * Last name
	 */
	last_name: string;
	/**
	 * Date of birth
	 */
	date_of_birth?: string;
	/**
	 * List of parliamentary terms
	 */
	terms: Array<number>;
	country: Country;
	/**
	 * The MEP’s political group at the time of the vote
	 */
	group?: Group;
	/**
	 * URL to the MEP’s official portrait photo
	 */
	photo_url: string;
	/**
	 * URL to a smaller, optimized variant of the official portrait photo
	 */
	thumb_url: string;
	/**
	 * Official email address
	 */
	email?: string;
	/**
	 * URL to the MEP’s Facebook profile
	 */
	facebook?: string;
	/**
	 * URL ot the MEP’s Twitter account
	 */
	twitter?: string;
};



/**
 * Political group in the European Parliament
 */
export type Group = {
	/**
	 * Unique identifier for the political group
	 */
	code: string;
	/**
	 * Name of the political group
	 */
	label: string;
	/**
	 * Short label or acronym of the political group
	 */
	short_label?: string;
};



/**
 * Country or territory published in the list of countries and territories by the
 * Publications Office of the European Union.
 */
export type Country = {
	/**
	 * Country code. If the country or territory is included in the ISO-3166-1 standard,
 * this is the 3-letter ISO-3166-1 code. Otherwise this is a custom code [as assigned by
 * the Publications Office of the European Union](https://op.europa.eu/en/web/eu-vocabularies/countries-and-territories).
	 */
	code: string;
	/**
	 * If the country or territory is included in the ISO-3166-1 standard, this is the two-
 * letter ISO-3166-1 code. Empty if the country is not included in the ISO-3166-1 standard.
	 */
	iso_alpha_2?: string;
	/**
	 * Name of the country or territory
	 */
	label: string;
};



/**
 * A concept from the [EuroVoc thesaurus](https://eur-lex.europa.eu/browse/eurovoc.html)
 */
export type EurovocConcept = {
	/**
	 * ID of the concept in the EuroVoc thesaurus
	 */
	id: string;
	/**
	 * Primary label of the concept in the EuroVoc thesaurus
	 */
	label: string;
};



export type PlenarySession = {
	id: string;
	/**
	 * Start date
	 */
	start_date: string;
	/**
	 * End date
	 */
	end_date: string;
	/**
	 * Whether this is a past, upcoming or current session
	 */
	status: 'CURRENT' | 'UPCOMING' | 'PAST';
	/**
	 * Location of the plenary session
	 */
	location?: 'SXB' | 'BRU';
};





export type PlenarySessionsQueryResponse = (QueryResponse & {
/**
 * Plenary sessions
 */
results: Array<PlenarySession>;
});



export type Vote = (BaseVote & {
/**
 * Information about the legislative procedure to which this vote belongs
 */
procedure?: Procedure;
/**
 * Facts about the vote. Usually an HTML formatted list of 3-4 bullet points extracted
 * from press releases published by the European Parliament.
 */
facts?: string;
/**
 * URL to a share picture for this vote.
 */
sharepic_url?: string;
/**
 * Statistics about this vote
 */
stats: VoteStats;
/**
 * List of MEPs and their vote positions
 */
member_votes: Array<MemberVote>;
/**
 * List of official sources for this data record
 */
sources: Array<Source>;
related: Array<RelatedVote>;
});



export type BaseVote = {
	/**
	 * ID as published in the official roll-call vote results
	 */
	id: number;
	/**
	 * Date and time of the vote
	 */
	timestamp: string;
	/**
	 * Title that can be used to refer to the vote. In most cases, this is the title
 * published in the roll-call vote results. If the title in the roll-call vote results
 * is empty, this falls back to the procedure title.
	 */
	display_title?: string;
	/**
	 * Reference to a plenary document such as a report or a resolution
	 */
	reference?: string;
	/**
	 * Description of the vote as published in the roll-call vote results
	 */
	description?: string;
	/**
	 * Whether this vote is featured. Currently, a vote is featured when we have found an
 * official press release about the vote published by the European Parliament Newsroom.
 * However, this is subject to change.
	 */
	is_featured: boolean;
	/**
	 * Countries or territories related to this vote
	 */
	geo_areas: Array<Country>;
	/**
	 * Concepts from the [EuroVoc](https://eur-lex.europa.eu/browse/eurovoc.html) thesaurus
 * that are related to this vote
	 */
	eurovoc_concepts: Array<EurovocConcept>;
};



/**
 * European Union legislative procedure
 */
export type Procedure = {
	/**
	 * Title of the legislative proceudre as listed in the Legislative Observatory
	 */
	title?: string;
	/**
	 * Procedure reference as listed in the Legislative Observatory
	 */
	reference: string;
};



export type VoteStats = {
	/**
	 * Total number of MEPs by vote position
	 */
	total: VotePositionCounts;
	/**
	 * Total number of MEPs by country and vote position
	 */
	by_country: Array<VoteStatsByCountry>;
	/**
	 * Total number of MEPs by political group and vote position
	 */
	by_group: Array<VoteStatsByGroup>;
};



export type VoteStatsByGroup = {
	group: Group;
	stats: VotePositionCounts;
};



export type VoteStatsByCountry = {
	country: Country;
	stats: VotePositionCounts;
};



export type VotePositionCounts = {
	FOR: number;
	AGAINST: number;
	ABSTENTION: number;
	DID_NOT_VOTE: number;
};



export type MemberVote = {
	member: Member;
	position: 'FOR' | 'AGAINST' | 'ABSTENTION' | 'DID_NOT_VOTE';
};




export type Source = {
	/**
	 * Source name
	 */
	name: string;
	/**
	 * Source URL
	 */
	url: string;
	/**
	 * Date and time when the source was last accessed
	 */
	accessed_at: string;
};



export type QueryResponse = {
	/**
	 * Total number of results. This is an approximate number and the exact number of search
 * results that are returned when paging through all results may be different.
	 */
	total: number;
	/**
	 * Search results page
	 */
	page: number;
	/**
	 * Number of results per page
	 */
	page_size: number;
	/**
	 * Whether there is a previous page of results
	 */
	has_prev: boolean;
	/**
	 * Whether there is a next page of results
	 */
	has_next: boolean;
};



export type VotesQueryResponse = (QueryResponse & {
/**
 * Votes
 */
results: Array<BaseVote>;
});



export type RelatedVote = {
	/**
	 * ID as published in the official roll-call vote results
	 */
	id: number;
	/**
	 * Date and time of the vote
	 */
	timestamp: string;
	/**
	 * Description of the vote as published in the roll-call vote results
	 */
	description?: string;
};



export type Statistics = {
	/**
	 * Total number of votes
	 */
	votes_total: number;
	/**
	 * Total number of members
	 */
	members_total: number;
	/**
	 * Total number of years since start of data collection
	 */
	years_total: number;
	/**
	 * Last data pipeline run time
	 */
	last_update_date: string;
};

