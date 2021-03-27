<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="{{ mix('css/app.css') }}" />

        <title>{{ $vote->display_title }} - Sharepic</title>
    </head>
    <body>
        <h1>{{ $vote->display_title }}</h1>
        <h2>{{ $vote->date->format('Y-m-d') }}</h2>
        <x-vote-result-chart :stats="$vote->stats" />
    </body>
</html>
