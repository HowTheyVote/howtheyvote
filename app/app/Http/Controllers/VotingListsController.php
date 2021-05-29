<?php

namespace App\Http\Controllers;

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

        return view('voting-lists.show', [
            'votingList' => $votingList,
            'members' => $members,
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
