@props(['title' => null])

<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="{{ mix('css/app.css') }}" />
        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">

        <script src="{{ mix('js/app.js') }}" async></script>

        <title>{{ $title }}</title>
    </head>
    <body>
        {{ $slot }}
    </body>
</html>
