<?php

namespace App\Http\Controllers;

use App\Vote;

class VotesController extends Controller
{
    public function sharePicture(Vote $vote)
    {
        return view('votes.share-picture', [
            'vote' => $vote,
        ]);
    }
}
