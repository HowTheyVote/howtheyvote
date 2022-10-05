@props([
    'member' => null,
    'group' => null,
    'lastActive' => null,
])

<div {{ $attributes->bem('member-header') }}>
    <x-wrapper class="member-header__wrapper">
        <img
            class="member-header__photo"
            src="{{ $member->profile_picture_url }}"
            alt="Photo of {{ $member->full_name }}"
        />

        <div class="member-header__text">
            <h1 class="member-header__title alpha">
                {{ $member->full_name }}
            </h1>

            <p class="member-header__subtitle">
                {{ $member->country->label }} {{ $member->country->emoji }}

                @if ($group && !$lastActive)
                    · 
                    {{ $group->name }}
                @else
                    · last active in 
                    {{ $group->name }}
                    in {{ $lastActive }}
                @endif
            </p>

            @if ($member->links->isNotEmpty())
                <ul class="member-header__social">
                    @foreach ($member->links as $type => $link)
                        <li>
                            <a
                                target="_blank"
                                rel="noopener noreferrer"
                                href="{!! $link !!}"
                            >
                                {{ ucfirst($type) }}
                            </a>
                        </li>
                    @endforeach
                </ul>
            @endif
        </div>
    </x-wrapper>
</div>

