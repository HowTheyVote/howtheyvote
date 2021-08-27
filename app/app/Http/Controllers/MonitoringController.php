<?php

namespace App\Http\Controllers;

use App\Vote;
use App\VotingList;

class MonitoringController extends Controller
{
    public function index()
    {
        $votes = Vote::whereDoesntHave('votingList')->get();
        $votingLists = VotingList::whereDoesntHave('vote')->get();

        return view('monitoring.index', [
            'votingLists' => $votingLists,
            'votes' => $votes,
        ]);
    }

    public function showLists($list)
    {
        $list = VotingList::find($list);

        return view('monitoring.show', [
            'record' => $list,
        ]);
    }

    public function showVotes($vote)
    {
        $vote = Vote::find($vote);

        return view('monitoring.show', [
            'record' => $vote,
        ]);
    }
}
