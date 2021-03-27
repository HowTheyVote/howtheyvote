<?php

namespace App\Actions;

use App\Vote;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class GenerateVoteSharePicAction extends Action
{
    public function execute(Vote $vote): void
    {
        $token = env('BROWSERLESS_TOKEN');
        $response = Http::post("https://chrome.browserless.io/screenshot?token={$token}", [
            'url' => route('vote.share-picture', ['vote' => $vote->id]),
            'options' => [
                'type' => 'png',
                'fullPage' => true,
            ],
            'viewport' => [
                'width' => 600,
                'height' => 315,
                'deviceScaleFactor' => 2,
            ],
        ]);

        Storage::disk('public')->put("vote-sharepic-{$vote->id}.png", $response->getBody());
    }
}
