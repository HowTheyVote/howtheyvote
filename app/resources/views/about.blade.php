<x-app :title="__('about.title')">
    <x-base-layout>
        <x-stack>

            <h1 class="alpha">{{ __('about.title') }}</h1>

            <p>{!! __('about.text')  !!}</p>

            <h2 class="beta">{{ __('about.headings.license')}}</h2>
            <p>{!! __('about.copyright-ep')  !!}</p>
            <p>{!! __('about.our-license')  !!}</p>

            <h2 class="beta">{{ __('about.headings.funding')}}</h2>
            <p>{!! __('about.funding')  !!}</p>

            <x-logos>
                <img src="/assets/logos/logo-bmbf.svg" alt="Federal Ministry of Education and Research">

                <img src="/assets/logos/logo-ptf.svg" alt="Prototype Fund">
            </x-logos>

        </x-stack>
    </x-base-layout>
</x-app>
