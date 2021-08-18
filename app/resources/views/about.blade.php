<x-app :title="__('about.title')">
    <x-base-layout>
        <x-stack>

            <h1 class="alpha">{{ __('about.title') }}</h1>

            <x-stack space="lg">
                <p>{!! __('about.text')  !!}</p>

                <p>{!! __('about.funding')  !!}</p>
            </x-stack>

            <x-logos>
                <img src="/assets/logos/logo-bmbf.svg" alt="Federal Ministry of Education and Research">

                <img src="/assets/logos/logo-ptf.svg" alt="Prototype Fund">
            </x-logos>

        </x-stack>
    </x-base-layout>
</x-app>
