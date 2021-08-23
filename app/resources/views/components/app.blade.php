@props([
    'title' => null,
    'sharePicture' => null,
    'sharePictureAlt' => null,
    'shareUrl' => null,
])

@php
    // Use default share picture if a falsy values is passed,
    // even if it is passed explicitly.
    $sharePicture = $sharePicture ?: asset('/assets/default-share-picture.png');
    $sharePictureAlt = $sharePictureAlt ?: __('share.default-share-picture.alt');
@endphp

<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="{{ mix('css/app.css') }}" />
        <script src="{{ mix('js/app.js') }}" async defer></script>

        <title>{{ $title }}</title>

        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="HowTheyVote.eu" />
        <meta property="og:title" content="{{ $title }}" />

        <meta property="twitter:site" content="{{ '@HowTheyVoteEu' }}" />
        <meta property="twitter:title" content="{{ $title }}" />

        @if ($shareUrl)
            <meta property="og:url" content="{{ $shareUrl }}" />
        @endif

        <meta property="og:image" content="{{ $sharePicture }}" />
        <meta property="og:image:alt" content="{{ $sharePictureAlt }}" />

        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:image" content="{{ $sharePicture }}" />
        <meta property="twitter:image:alt" content="{{ $sharePictureAlt }}" />
    </head>
    <body>
        {{ $slot }}
    </body>
</html>
