<div {{ $attributes->bem('footer') }}>
    <ul>
        <li>
            <a
                href="https://github.com/HowTheyVote/epvotes"
                target="_blank"
                rel="noopener noreferrer"
            >
                Source Code
            </a>
        </li>
        <li>
            <a href="{{ url('/about') }}">
                {{ __('about.title') }}
            </a>
        </li>
        <li>
            <a href="{{ url('/imprint') }}">
                {{ __('imprint.title') }}
            </a>
        </li>
    </ul>
</div>
