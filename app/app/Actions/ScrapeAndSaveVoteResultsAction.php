<?php

namespace App\Actions;

use App\Document;
use App\Enums\DocumentTypeEnum;
use App\Enums\VotePositionEnum;
use App\Member;
use App\Term;
use App\Vote;
use Illuminate\Support\Carbon;

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
            'document_id' => $document->id,
        ]);

        $this->createOrUpdateVotings($date, $vote, $data['votings']);

        return $vote;
    }

    protected function findOrCreateDocument(array $data): Document
    {
        $term = Term::whereNumber($data['term'])->first();

        return Document::firstOrCreate([
            'type' => DocumentTypeEnum::make($data['type']),
            'term_id' => $term->id,
            'number' => $data['number'],
            'year' => $data['year'],
        ]);
    }

    protected function createOrUpdateVotings(Carbon $date, Vote $vote, array $votings): void
    {
        $members = collect($votings)->map(function ($voting) use ($date) {
            $member = $this->findMember($date, $voting);
            $position = VotePositionEnum::make($voting['position']);

            return [$member->id, ['position' => $position]];
        })->toAssoc();

        $vote->members()->sync($members);
    }

    protected function findMember(Carbon $date, array $voting): Member
    {
        $activeMembers = Member::activeAt($date);

        // The official vote results provided by the parliament
        // only contain member's last names. Only if the last name
        // is ambiguous (i.e. there are two members with the same
        // last name active in parliament at the same time), the
        // respective first and last names are listed.
        $member = (clone $activeMembers)
            ->whereLastName($voting['name'])
            ->first();

        if ($member) {
            return $member;
        }

        return (clone $activeMembers)
            ->whereRaw('first_name || " " || last_name = ?', [$voting['name']])
            ->first();
    }
}
