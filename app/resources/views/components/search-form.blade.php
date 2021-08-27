<form class="search-form" method="get" action="/votes">
    <x-search-input class="search-form__input" />
    <x-button
        type="submit"
        size="lg"
        style="fill"
        class="search-form__submit"
    >
        {{ __('components.search-form.submit') }}
    </x-button>
</form>
