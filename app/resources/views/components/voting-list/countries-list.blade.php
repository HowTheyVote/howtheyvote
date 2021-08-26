@props(['countries'])

<x-list
    :truncate="true"
    :show-more="__('voting-lists.countries.show-more')"
    :searchable="true"
    :search-placeholder="__('voting-lists.countries.search-placeholder')"
>
    @foreach ($countries as $country => $stats)
        <x-country-list-item
            :country="\App\Enums\CountryEnum::make($country)"
            :stats="$stats"
        />
    @endforeach
</x-list>
