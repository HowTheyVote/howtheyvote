@props(['size' => null])

<button {{ $attributes->bem('button', $size) }}>
    {{ $slot }}
</button>
