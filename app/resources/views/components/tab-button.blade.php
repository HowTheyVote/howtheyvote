@props([
    'id' => null,
    'selected' => false,
])

<button
    type="button"
    id="tab-members"
    role="tab"
    class="tab-button"
    @if($selected) aria-selected="true" @endif
    @if(!$selected) tabindex="-1" @endif
>
    {{ $slot }}
</button>
