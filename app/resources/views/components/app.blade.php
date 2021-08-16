@props([
    'title' => null,
    'padding' => false,
    'sharePicture' => null,
])

<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        @if ($sharePicture)
            <meta property="og:image" content="{{ $sharePicture }}" />
            <meta property="twitter:card" content="summary_large_image" />
            <meta property="twitter:image" content="{{ $sharePicture }}" />
        @endif

        <link rel="stylesheet" href="{{ mix('css/app.css') }}" />
        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">

        <script src="{{ mix('js/app.js') }}" async defer></script>

        <title>{{ $title }}</title>
    </head>
    <body {{ $padding == true ? 'class=padding' : ""}}>
        {{ $slot }}
    </body>
</html>
