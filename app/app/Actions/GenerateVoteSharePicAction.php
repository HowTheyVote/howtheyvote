<?php

namespace App\Actions;

use App\VotingList;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class GenerateVoteSharePicAction extends Action
{
    public function execute(VotingList $votingList): void
    {
        $exists = Storage::disk('public')->exists("vote-sharepic-{$votingList->id}.png");

        if ($exists) {
            return;
        }

        $token = config('browserless.token');
        $response = Http::post("https://chrome.browserless.io/screenshot?token={$token}", [
            'url' => route('voting-list.share-picture', ['votingList' => $votingList->id]),
            'options' => [
                'type' => 'png',
                'fullPage' => true,
            ],
            'gotoOptions' => [
                'waitUntil' => 'networkidle0',
            ],
            'viewport' => [
                'width' => 600,
                'height' => 315,
                'deviceScaleFactor' => 2,
            ],
        ]);

        Storage::disk('public')->put("vote-sharepic-{$votingList->id}.png", $response->getBody());
    }
}
