<?php

namespace App\Http\Controllers;

use App\Enums\CountryEnum;
use App\Group;
use App\VotingList;
use Spatie\SimpleExcel\SimpleExcelWriter;
use Spatie\Url\Url;
use Vinkla\Hashids\Facades\Hashids;

class VotingListsController extends Controller
{
    public function index()
    {
        return view('voting-lists.index');
    }

    public function show(VotingList $votingList)
    {
        $stats = $votingList->stats;

        $groups = Group::all()
            ->map(function ($group) use ($stats) {
                $group->stats = $stats['by_group'][$group->id] ?? null;

                return $group;
            })
            ->filter(function ($group) {
                return $group->stats && $group->stats['active'] > 0;
            })
            ->sortByDesc(function ($group) {
                return $group->stats['active'];
            });

        $countries = collect(CountryEnum::toValues())
            ->map(function ($country) use ($stats) {
                $countryStats = $stats['by_country'][$country] ?? null;

                return [$country, $countryStats];
            })
            ->toAssoc()
            ->filter(function ($countryStats) {
                return $countryStats && $countryStats['active'] > 0;
            })
            ->sortByDesc(function ($countryStats) {
                return $countryStats['active'];
            });

        return view('voting-lists.show', [
            'votingList' => $votingList,
            'members' => $this->members($votingList),
            'groups' => $groups,
            'countries' => $countries,
        ]);
    }

    public function summary(VotingList $votingList)
    {
        if (! $votingList->vote->summary) {
            return abort(404);
        }

        if (! $votingList->vote->isFinalVote()) {
            return abort(404);
        }

        return view('voting-lists.summary', [
            'votingList' => $votingList,
            'summary' => $votingList->vote->summary,
        ]);
    }

    public function related(VotingList $votingList)
    {
        if (! $votingList->vote) {
            return abort(404);
        }

        if (! $votingList->vote->isFinalVote()) {
            return abort(404);
        }

        $relatedVotes = $votingList->vote
            ->relatedVotes()
            ->with('votingList')
            ->get();

        return view('voting-lists.related', [
            'votingList' => $votingList,
            'relatedVotes' => $relatedVotes,
        ]);
    }

    public function sharePicture(VotingList $votingList)
    {
        $shortUrl = Url::fromString(route('voting-list.short', ['hashId' => $votingList->hashId]));
        $shortDisplayUrl = $shortUrl->getHost().$shortUrl->getPath();

        return view('voting-lists.share-picture', [
            'votingList' => $votingList,
            'shortDisplayUrl' => $shortDisplayUrl,
        ]);
    }

    public function csv(VotingList $votingList)
    {
        $rows = $this->members($votingList)->map(function ($member) {
            return [
                'member_id' => $member->id,
                'last_name' => $member->last_name,
                'first_name' => $member->first_name,
                'group.abbreviation' => $member->group->abbreviation,
                'group.name' => $member->group->name,
                'country.code' => $member->country->value,
                'country.name' => $member->country->label,
                'position' => $member->pivot->position->label,
            ];
        })->toArray();

        ob_start();
        $writer = SimpleExcelWriter::createWithoutBom('php://output', 'csv');
        $writer->addRows($rows)->close();
        $csv = ob_get_clean();

        return response($csv, 200, ['Content-Type' => 'text/csv']);
    }

    public function json(VotingList $votingList)
    {
        $members = $this->members($votingList)->map(function ($member) {
            return [
                'member_id' => $member->id,
                'last_name' => $member->last_name,
                'first_name' => $member->first_name,
                'group' => [
                    'abbreviation' => $member->group->abbreviation,
                    'name' => $member->group->name,
                ],
                'country' => [
                    'code' => $member->country->value,
                    'name' => $member->country->label,
                ],
                'position' => $member->pivot->position->label,
            ];
        })->toArray();

        $vote = [
            'title' => $votingList->display_title,
            'date' => $votingList->date,
            'result' => $votingList->result->label,
            'members' => $members,
        ];

        return response()->json($vote);
    }

private function members(VotingList $votingList)
    {
        return $votingList
            ->members()
            ->withGroupMembershipAt($votingList->date)
            ->with('group')
            // Select only specific attributes of joined tables
            // as otherwise e.g. `group_memberships.id` would overwrite
            // `members.id`.
            ->select('members.*', 'votings.position', 'group_memberships.group_id')
            ->get();
    }

    public function short(string $hashId)
    {
        $votingList = VotingList::find(Hashids::decode($hashId))->first();

        if (! $votingList) {
            abort(404);
        }

        return redirect()->route('voting-list.show', ['votingList' => $votingList->id]);
    }
}
