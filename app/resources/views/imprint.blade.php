<x-app :title="__('imprint.title')">
    <x-base-layout>
        <x-stack>
            <h1 class="alpha">
                {{ __('imprint.title') }}
            </h1>

            <x-stack space="sm">
                <p>
                    {{ __('imprint.name') }}<br>
                    {{ __('imprint.street') }}<br>
                    {{ __('imprint.city') }}
                </p>
                <p>
                    {{ __('imprint.email') }}<br>
                    {{ __('imprint.tax-id') }}
                </p>
                <p>{{ __('imprint.privacy') }}</p>
            </x-stack>
        </x-stack>
    </x-base-layout>
</x-app>
