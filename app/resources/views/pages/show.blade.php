<x-app :title="$page->title">
    <x-base-layout>
        <div class="padding--h padding--v">
            <x-wrapper>
                <x-stack>
                    <h1 class="alpha">
                        {{ $page->title }}
                    </h1>

                    <x-markdown :parse="false">
                        {{ $page->contents }}
                    </x-markdown>
                </x-stack>
            </x-wrapper>
        </div>
    </x-base-layout>
</x-app>
