<div class="share-picture">
    <main class="share-picture__content">
        {{ $slot }}
    </main>

    <footer class="share-picture__footer">
        <div class="share-picture__footer-text">
            {{ $footer }}
        </div>
        <x-cc-logo class="share-picture__cc-logo" modifiers="light" />
    </footer>
</div>
