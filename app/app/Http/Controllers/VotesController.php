<?php

namespace App\Http\Controllers;

use App\Vote;
use Spatie\Url\Url;

class VotesController extends Controller
{
    public function sharePicture(Vote $vote)
    {
        $shortUrl = Url::fromString(route('vote.short', ['hashId' => $vote->hashId]));
        $shortDisplayUrl = $shortUrl->getHost().$shortUrl->getPath();

        return view('votes.share-picture', [
            'vote' => $vote,
            'shortDisplayUrl' => $shortDisplayUrl,
        ]);
    }
}
