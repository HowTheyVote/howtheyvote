<?php

namespace App\Actions;

use App\Member;
use Illuminate\Support\Facades\Storage;
use Intervention\Image\Exception\NotReadableException;
use Intervention\Image\Facades\Image;

class CreateMemberThumbnailAction extends Action
{
    public function execute(Member $member): void
    {
        $url = "https://www.europarl.europa.eu/mepphoto/{$member->web_id}.jpg";

        $width = 104;
        $quality = 50;

        $path = "members/{$member->id}-{$width}px.jpg";

        try {
            $thumb = Image::make($url)
                ->widen($width)
                ->crop($width, $width)
                ->encode('jpg', $quality);

            Storage::disk('public')->put($path, $thumb);
        } catch (NotReadableException $exception) {
            // It’s most likely that the parliament website returned a
            // 404 error code when requesting the original image.
        }
    }
}
