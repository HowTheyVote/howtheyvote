<x-app :title="__('about.title')">
    <x-base-layout>
        <div class="padding--h padding--v">
            <x-wrapper>
                <x-stack>
                    <h1 class="alpha">{{ __('about.title') }}</h1>

                        <x-markdown>
{{ __('about.parliament')  }}

{{ __('about.parliamentary-informations')  }}

{{ __('about.goal')  }}

{{ __('about.headings.contact') }}
{{ __('about.outreach')  }}

{{ __('about.disclaimer')  }}

{{ __('about.headings.license')}}
{{ __('about.copyright-ep')  }}

{{ __('about.our-license')  }}

{{ __('about.headings.funding') }}
{{ __('about.funding')  }}
                        </x-markdown>

                    <x-logos>
                        <img src="/assets/logos/logo-bmbf.svg" alt="Federal Ministry of Education and Research">
                        <img src="/assets/logos/logo-ptf.svg" alt="Prototype Fund">
                    </x-logos>
                </x-stack>
            </x-wrapper>
        </div>
    </x-base-layout>
</x-app>
