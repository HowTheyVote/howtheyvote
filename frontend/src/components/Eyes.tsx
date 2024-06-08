import { useEffect, useRef, useState } from "preact/hooks";

// The radius of the circle the pupils should move along
const RADIUS = 10;

// Hardcoded dimensions of the eye/white ellipsis. As we're
// using SVG symbols, the actual DOM elements are placed inside
// a shadow DOM which makes it impossible to get the dimensions
// dynamically.
const WIDTH = 35;
const HEIGHT = 45;

type EyeProps = {
  translateX: number;
  translateY: number;
};

function Eye({ translateX, translateY }: EyeProps) {
  const ref = useRef<SVGGElement | null>(null);
  const bounds = ref.current?.getBoundingClientRect();

  const centerX = (bounds?.x || 0) + WIDTH / 2;
  const centerY = (bounds?.y || 0) + HEIGHT / 2;

  const [cursorX, setCursorX] = useState(0);
  const [cursorY, setCursorY] = useState(0);

  const onMouseMove = (event: MouseEvent) => {
    setCursorX(event.pageX);
    setCursorY(event.pageY);
  };

  useEffect(() => {
    window.addEventListener("mousemove", onMouseMove);
    return () => window.removeEventListener("mousemove", onMouseMove);
  }, []);

  // Relative position of the cursor from the center of the eye
  let x = cursorX - centerX;
  let y = cursorY - centerY;

  const angle = Math.atan2(x, y);

  // Point on circumference of a circle around the center of the eye
  const circleX = Math.round(RADIUS * Math.sin(angle));
  const circleY = Math.round(RADIUS * Math.cos(angle));

  // Limit the position to the circle
  x = Math.max(-1 * Math.abs(circleX), Math.min(circleX, x));
  y = Math.max(-1 * Math.abs(circleY), Math.min(circleY, y));

  return (
    <g ref={ref} transform={`translate(${translateX} ${translateY})`}>
      <use xlinkHref="#white" />
      <use xlinkHref="#pupil" transform={`translate(${x} ${y})`} />
    </g>
  );
}

export default function Eyes() {
  return (
    <div class="eyes">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        xmlnsXlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 300 300"
        width="150px"
        height="150px"
      >
        <title>
          The stars of the EU flag with two eyes inside, which together form a
          face.
        </title>
        <defs>
          <path
            id="star"
            d="M21 29L8.7 38l4.7-14.5-12.4-9h15.3L21 0l4.7 14.6H41l-12.4 8.9L33.3 38z"
            fill="#FFCC00"
            transform="translate(-20 -20)"
          />

          <ellipse
            id="white"
            cx="30"
            cy="45"
            rx="30"
            ry="45"
            fill="#fff"
            filter="url(#inset-shadow)"
          />

          <symbol id="pupil">
            <g class="pupil">
              <circle id="outer" cx="30" cy="45" r="15" fill="#875500" />
              <circle id="inner" cx="30" cy="45" r="11" fill="#281201" />
              <ellipse
                id="reflection"
                cx="25"
                cy="37.5"
                rx="2"
                ry="3"
                fill="#fff"
              />
            </g>
          </symbol>

          <filter id="inset-shadow">
            <feOffset dx="0" dy="2" />
            <feGaussianBlur stdDeviation="5" result="offset-blur" />
            <feComposite
              operator="out"
              in="SourceGraphic"
              in2="offset-blur"
              result="inverse"
            />
            <feFlood flood-color="black" flood-opacity="1" result="color" />
            <feComposite
              operator="in"
              in="color"
              in2="inverse"
              result="shadow"
            />
            <feComposite operator="over" in="shadow" in2="SourceGraphic" />
          </filter>
        </defs>

        <g id="stars" transform="translate(150 150)">
          <use x="113" y="65" xlinkHref="#star" />
          <use x="65" y="113" xlinkHref="#star" />
          <use x="0" y="130" xlinkHref="#star" />
          <use x="-65" y="113" xlinkHref="#star" />
          <use x="-113" y="65" xlinkHref="#star" />
          <use x="-130" y="0" xlinkHref="#star" />
          <use x="-113" y="-65" xlinkHref="#star" />
          <use x="-65" y="-113" xlinkHref="#star" />
          <use x="0" y="-130" xlinkHref="#star" />
          <use x="65" y="-113" xlinkHref="#star" />
          <use x="113" y="-65" xlinkHref="#star" />
          <use x="130" y="0" xlinkHref="#star" />
        </g>

        <g id="eyes" transform="translate(150 120)">
          <Eye translateX={-65} translateY={-45} />
          <Eye translateX={5} translateY={-45} />
        </g>
      </svg>
    </div>
  );
}
