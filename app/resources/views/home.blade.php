<x-app title="HowTheyVote.eu">
    <x-base-layout style="dark">
        <div class="home">
            <div class="home__wrapper">
                <h1 class="home__title">
                    {{ __('components.home.title') }}
                </h1>
                <x-search-form />
                <div class="home__hint">
                    {!! __('components.home.hint') !!}
                </div>
            </div>
        </div>
    </x-base-layout>
</x-app>
