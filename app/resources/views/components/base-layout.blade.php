@props(['style' => null])

<div {{ $attributes->bem('base-layout', $style) }}>
    <x-header :style="$style" />

    <main class="base-layout__main">
        {{ $slot }}
    </main>
    <x-wrapper class="base-layout__footer">
        <x-footer :style="$style">
            @if ($style === 'dark')
                <p>
                    Photo: © European Union 2019 ·
                    <a
                        href="https://multimedia.europarl.europa.eu/en/stockshot-of-hemicycle-of-european-parliament-in-strasbourg-vote-by-show-of-hand_20191023_EP-094585E_FMA_047_p"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Source: EP/Fred MARVAUX
                    </a>
                </p>
            @endif
        </x-footer>
    </x-wrapper>
</div>
