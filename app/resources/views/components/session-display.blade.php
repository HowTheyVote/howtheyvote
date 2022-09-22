@props([
    'currentSession' => null,
    'lastSession' => null,
    'nextSession' => null,
])


@if ($currentSession)

    <div {{ $attributes->bem('session-display') }}>
        {{ __('components.session-display.current', [
            'location' => $currentSession->location->label(),
        ]) }}

        {!! __('components.session-display.agenda', [
            'agenda' => $currentSession->agenda_url]) !!}</br>

        {{ __('components.session-display.availability') }}
    </div>

@elseif ($lastSession && $lastSession->votes()->matched()->final()->count() <= 0)

    <div {{ $attributes->bem('session-display') }}>
        {!! __('components.session-display.last', [
            'start' => $lastSession->start_date->format('M jS'),
            'end' =>$lastSession->end_date->format('M jS'),
            'location' => $lastSession->location->label(),
        ]) !!}

        {!! __('components.session-display.agenda', [
            'agenda' => $lastSession->agenda_url]) !!}</br>

        {{ __('components.session-display.availability') }}
    </div>

@elseif ($nextSession)

    <div {{ $attributes->bem('session-display') }}>
        {!! __('components.session-display.next', [
            'start' => $nextSession->start_date->format('M jS'),
            'end' =>$nextSession->end_date->format('M jS'),
            'location' => $nextSession->location->label(),
        ]) !!}

        {!! __('components.session-display.agenda', [
            'agenda' => $nextSession->agenda_url]) !!}</br>
        
        {{ __('components.session-display.availability') }}
    </div>

@endif
