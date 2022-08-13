@props([
    'name' => null,
    'xModel' => null,
    'label' => 'Filter',
    'reset' => 'Show all',
])

<details class="position-select" {{ $attributes }}>
  <x-button tag="summary" class="position-select__button">
    <span data-menu-button>{{ $label }}</span>
  </x-button>

  <details-menu role="menu" class="position-select__menu">
      <label
        tabindex="0"
        role="menuitemradio"
        class="position-select__item position-select__reset"
        aria-checked="true"
    >
        <input
            type="radio"
            class="visually-hidden"
            name="{{ $name }}"
            x-model="{{ $xModel }}"
            value=""
            checked
        />

        {{ $reset }}

        <span data-menu-button-contents hidden>
            {{ $label }}
        </span>
    </label>

    @foreach (\App\Enums\VotePositionEnum::cases() as $position)
      <label
        tabindex="0"
        role="menuitemradio"
        class="position-select__item"
    >
        <input
            type="radio"
            class="visually-hidden"
            name="{{ $name }}"
            x-model="{{ $xModel }}"
            value="{{ $position->label }}"
        />

        <span data-menu-button-contents>
            <span class="position-select__label">
                <x-thumb :position="$position" style="circle" />
                {{ $position->label }}
            </span>
        </span>
      </label>
    @endforeach
  </details-menu>
</details>
