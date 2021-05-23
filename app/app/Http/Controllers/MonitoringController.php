<?php

namespace App\Http\Controllers;

use App\VotingList;

class MonitoringController extends Controller
{
    public function index()
    {
        $votingLists = VotingList::whereDoesntHave('vote')->get();

        return view('monitoring.index', [
            'votingLists' => $votingLists,
        ]);
    }
}
