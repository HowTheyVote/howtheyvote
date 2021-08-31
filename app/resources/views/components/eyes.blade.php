<div class="eyes">
    <svg
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 300 300"
        width="150px"
        height="150px"
    >
        <defs>
            <path id="star" d="M21 29L8.7 38l4.7-14.5-12.4-9h15.3L21 0l4.7 14.6H41l-12.4 8.9L33.3 38z" fill="#FFCC00" transform="translate(-20 -20)" />

            <ellipse id="white" cx="30" cy="45" rx="30" ry="45" fill="#fff" filter="url(#inset-shadow)" />

            <symbol id="pupil">
                <g class="pupil" x-bind:transform="`translate(${translate.x}px ${translate.y}px)`">
                    <circle id="outer" cx="30" cy="45" r="15" fill="#875500" />
                    <circle id="inner" cx="30" cy="45" r="11" fill="#281201" />
                    <ellipse id="reflection" cx="25" cy="37.5" rx="2" ry="3" fill="#fff" />
                </g>
            </symbol>

            <filter id="inset-shadow">
                <feOffset dx="0" dy="2"/>
                <feGaussianBlur stdDeviation="5" result="offset-blur"/>
                <feComposite operator="out" in="SourceGraphic" in2="offset-blur" result="inverse"/>
                <feFlood flood-color="black" flood-opacity="1" result="color"/>
                <feComposite operator="in" in="color" in2="inverse" result="shadow"/>
                <feComposite operator="over" in="shadow" in2="SourceGraphic"/>
            </filter>
        </defs>

        <g id="stars" transform="translate(150 150)">
            <use x="113" y="65" xlink:href="#star" />
            <use x="65" y="113" xlink:href="#star" />
            <use x="0" y="130" xlink:href="#star" />
            <use x="-65" y="113" xlink:href="#star" />
            <use x="-113" y="65" xlink:href="#star" />
            <use x="-130" y="0" xlink:href="#star" />
            <use x="-113" y="-65" xlink:href="#star" />
            <use x="-65" y="-113" xlink:href="#star" />
            <use x="0" y="-130" xlink:href="#star" />
            <use x="65" y="-113" xlink:href="#star" />
            <use x="113" y="-65" xlink:href="#star" />
            <use x="130" y="0" xlink:href="#star" />
        </g>

        <g id="eyes" transform="translate(150 120)">
            <g transform="translate(-65 -45)">
                <use xlink:href="#white" />
                <use
                    xlink:href="#pupil"
                    x-data="eye"
                    x-on:resize.window="setCenterPosition()"
                    x-on:mousemove.window="setCursorPosition($event)"
                    x-bind:transform="`translate(${translate.x} ${5 + translate.y})`"
                />
            </g>

            <g transform="translate(5 -45)">
                <use xlink:href="#white" />
                <use
                    xlink:href="#pupil"
                    x-data="eye"
                    x-on:resize.window="setCenterPosition()"
                    x-on:mousemove.window="setCursorPosition($event)"
                    x-bind:transform="`translate(${translate.x} ${5 + translate.y})`"
                />
            </g>
        </g>
    </svg>
</div>
