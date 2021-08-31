@props(['title', 'message'])

<div {{ $attributes->bem('error-page') }}>
    <div class="error-page__wrapper">
        <x-eyes />
        <h1 class="error-page__title alpha">
            {{ $title }}
        </h1>
        <p class="error-page__message">
            {!! $message !!}
        </p>
    </div>
</div>
