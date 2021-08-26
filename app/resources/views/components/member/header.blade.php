@props([
    'member' => null,
    'group' => null
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

                @if ($group)
                    ·
                    {{ $group->name }}
                @endif
            </p>

            @if ($member->email || $member->twitter || $member->facebook)
                <ul class="member-header__social">
                    @if ($member->email)
                        <li>
                            <a href="mailto:{{ $member->email }}">
                                E-Mail
                            </a>
                        </li>
                    @endif

                    @if ($member->twitter)
                        <li>
                            <a href="{{ $member->twitter }}" target="_blank" rel="noopener noreferrer">
                                Twitter
                            </a>
                        </li>
                    @endif

                    @if ($member->facebook)
                        <li>
                            <a href="{{ $member->facebook }}" target="_blank" rel="noopener noreferrer">
                                Facebook
                            </a>
                        </li>
                    @endif
                </ul>
            @endif
        </div>
    </x-wrapper>
</div>

