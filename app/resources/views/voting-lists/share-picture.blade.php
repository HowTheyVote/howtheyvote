<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="{{ mix('css/app.css') }}" />
        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">

        <title>{{ $votingList->display_title }} - Sharepic</title>
    </head>
    <body>
        <x-share-picture>
            <x-stack space="sm">
                <x-stack space="xxs">
                    <h1 class="beta">{{ $votingList->display_title }}</h1>
                    <p class="text--xs">
                        @lang('voting-lists.share-picture.subtitle', [
                            'date' => $votingList->date->formatLocalized('%b %e, %Y'),
                        ])
                    </p>
                </x-stack>
                <x-vote-result-chart :stats="$votingList->stats" />
            </x-stack>

            <x-slot name="footer">
                {{ __('voting-lists.share-picture.footer') }}<br>
                <strong>{{ $shortDisplayUrl }}</strong>
            </x-slot>
        </x-share-picture>
    </body>
</html>
