<?php

namespace App\Actions;

use App\Member;
use Illuminate\Support\Facades\Storage;
use Intervention\Image\Exception\NotReadableException;
use Intervention\Image\Facades\Image;

class CreateMemberImageAction extends Action
{
    public function execute(Member $member): void
    {
        $url = "https://www.europarl.europa.eu/mepphoto/{$member->web_id}.jpg";

        $width = 104;
        $quality = 50;

        $pathSmall = "members/{$member->id}-{$width}px.jpg";
        $pathOrig = "members/{$member->id}.jpg";

        try {
            $thumbSmall = Image::make($url)
                ->widen($width)
                ->crop($width, $width)
                ->encode('jpg', $quality);

            $original = Image::make($url)
                ->encode('jpg', 65);

            Storage::disk('public')->put($pathSmall, $thumbSmall);
            Storage::disk('public')->put($pathOrig, $original);
        } catch (NotReadableException $exception) {
            // It’s most likely that the parliament website returned a
            // 404 error code when requesting the original image.
        }
    }
}
