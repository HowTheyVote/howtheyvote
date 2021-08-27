@props(['style' => null])

<div {{ $attributes->bem('base-layout', $style) }}>
    <x-header :style="$style" />

    <main class="base-layout__main">
        {{ $slot }}
    </main>
    <x-wrapper class="base-layout__footer">
        <x-footer :style="$style" />
    </x-wrapper>
</div>
