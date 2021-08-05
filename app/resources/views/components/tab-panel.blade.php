@props([
    'id' => null,
    'selected' => false,
])

<div
    role="tabpanel"
    aria-labelledby="tab-{{ $id }}"
    @if(!$selected) hidden @endif
>
   {{ $slot }}
</div>
