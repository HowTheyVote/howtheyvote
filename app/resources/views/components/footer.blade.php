@props(['style'])

<x-stack space="xxs" {{ $attributes->bem('footer', $style) }}>
    <ul>
        <li>
            <a
                href="https://github.com/HowTheyVote/epvotes"
                target="_blank"
                rel="noopener noreferrer"
            >
                GitHub
            </a>
        </li>
        <li>
            <a
                href="https://twitter.com/HowTheyVoteEU"
                target="_blank"
                rel="noopener noreferrer"
            >
                Twitter
            </a>
        </li>
        <li>
            <a href="{{ url('/pages/imprint') }}">
                {{ __('components.footer.nav.imprint') }}
            </a>
        </li>
    </ul>

    {{ $slot }}
</x-stack>
