<div class="base-layout">
    <x-header/>

    <main class="base-layout__main">
        <x-wrapper>
            {{ $slot }}
        </x-wrapper>
    </main>
    <x-wrapper class="base-layout__footer">
        <x-footer />
    </x-wrapper>
</div>
