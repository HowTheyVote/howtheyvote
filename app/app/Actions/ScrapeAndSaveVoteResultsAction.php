<?php

namespace App\Actions;

use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Enums\VotePositionEnum;
use App\Member;
use App\Term;
use App\Vote;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;

class ScrapeAndSaveVoteResultsAction
{
    private $scrapeAction;

    public function __construct(ScrapeAction $scrapeAction)
    {
        $this->scrapeAction = $scrapeAction;
    }

    public function execute(Term $term, Carbon $date): void
    {
        $response = $this->scrapeAction->execute('vote_results', [
            'term' => $term->number,
            'date' => $date->toDateString(),
        ]);

        foreach ($response as $data) {
            $this->createOrUpdateVote($term, $date, $data);
        }
    }

    protected function createOrUpdateVote(Term $term, Carbon $date, array $data): Vote
    {
        $document = $this->findOrCreateDocument($data['reference']);

        $vote = Vote::firstOrCreate([
            'doceo_vote_id' => $data['doceo_vote_id'],
            'term_id' => $term->id,
            'date' => $date,
        ]);

        $vote->update([
            'description' => $data['description'],
            'document_id' => $document->id ?? null,
        ]);

        // Preload a list of all active members on the day
        $members = $this->buildMembersLookup($date);

        $this->createOrUpdateVotings($members, $date, $vote, $data['votings']);

        return $vote;
    }

    protected function findOrCreateDocument(?array $data): ?Document
    {
        if (! $data) {
            return null;
        }

        $term = Term::whereNumber($data['term'])->first();

        return Document::firstOrCreate([
            'type' => DocumentTypeEnum::make($data['type']),
            'term_id' => $term->id,
            'number' => $data['number'],
            'year' => $data['year'],
        ]);
    }

    protected function createOrUpdateVotings(
        Collection $members,
        Carbon $date,
        Vote $vote,
        array $votings
    ): void {
        $memberVotes = [];

        foreach ($votings as $voting) {
            $member = $this->findMember($members, $date, $voting);
            $position = VotePositionEnum::make($voting['position']);

            $memberVotes[$member->id] = [
                'position' => $position,
            ];
        }

        $vote->members()->sync($memberVotes);
    }

    protected function findMember(Collection $members, Carbon $date, array $voting): Member
    {
        $name = Member::normalizeName($voting['name']);

        // The official vote results provided by the parliament
        // only contain member's last names. Only if the last name
        // is ambiguous (i.e. there are two members with the same
        // last name active in parliament at the same time), the
        // respective first and last names are listed.
        $member = $members->first(function ($member) use ($name) {
            return $member->last_name_normalized == $name;
        });

        if ($member) {
            return $member;
        }

        return $members->first(function ($member) use ($name) {
            $fullName = "{$member->last_name_normalized} {$member->first_name_normalized}";

            return $fullName == $name;
        });
    }

    protected function buildMembersLookup(Carbon $date): Collection
    {
        return Member::activeAt($date)
            ->select('id', 'first_name_normalized', 'last_name_normalized')
            ->get();
    }
}
