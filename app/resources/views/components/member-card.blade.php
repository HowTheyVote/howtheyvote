@props(['member' => null])

<div {{ $attributes->bem('member-card') }}>
    <img src="https://www.europarl.europa.eu/mepphoto/{{ $member->web_id }}.jpg"/>
</div>

