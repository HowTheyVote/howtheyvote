@props([
    'member' => null,
    'group' => null
])

<section {{ $attributes->bem('member-card') }}>
    <img src="{{ $member->profile_picture_url }}"/>
    <div>
        <x-stack space="xs" class="member-card__infos">
            <h1 class="alpha">{{ $member->full_name }}</h1>
            <p><strong>{{ __('members.headings.country') }}</strong> {{ $member->country->emoji }} {{ $member->country->label }}</p>
            <p>
                <strong>
                    {{ __('members.headings.group') }}
                </strong>
                @if($group)
                    {{ $group->name }}
                @else
                    {{ __('members.no-group') }}
                @endif
            </p>

            <ul class="member-card__contacts">
                @if ($member->email)
                    <li>
                        <a href="mailto:{{ $member->email }}">E-Mail</a>
                    </li>
                @endif

                @if ($member->twitter)
                    <li>
                        <a href="{{ $member->twitter }}" target="_blank" rel="noopener noreferrer" >Twitter</a>
                    </li>
                @endif

                @if ($member->facebook)
                    <li>
                        <a href="{{ $member->facebook }}" target="_blank" rel="noopener noreferrer" >Facebook</a>
                    </li>
                @endif
            </ul>
        </x-stack>

    </div>
</section>

