<?php

namespace App\Http\Controllers;

use App\Group;
use App\VotingList;
use Spatie\Url\Url;

class VotingListsController extends Controller
{
    public function show(VotingList $votingList)
    {
        $members = $votingList
            ->members()
            ->withGroupMembershipAt($votingList->date)
            ->with('group')
            ->select('*')
            ->get();

        $stats = $votingList->stats;

        $groups = Group::all()
            ->map(function ($group) use ($stats) {
                $group->stats = $stats['by_group'][$group->id] ?? null;

                return $group;
            })
            ->filter(function ($group) {
                return $group->stats && $group->stats['active'] > 0;
            });

        return view('voting-lists.show', [
            'votingList' => $votingList,
            'members' => $members,
            'groups' => $groups,
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
}
