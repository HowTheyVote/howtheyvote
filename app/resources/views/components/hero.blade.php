@props([
    'title',
    'text',
    'action' => null,
])

<div class="hero">
    <div class="padding--h">
        <x-wrapper class="hero__text">
            <h1 class="alpha hero__title">
                {{ $title }}
            </h1>

            <p>{{ $text }}</p>
        </x-wrapper>
    </div>

    @if ($action)
        <div class="hero__action padding--h">
            <x-wrapper>
                {{ $action }}
            </x-wrapper>
        </div>
    @endif
</div>
